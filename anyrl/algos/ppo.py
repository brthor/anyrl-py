"""
Proximal policy optimization.
"""

import tensorflow as tf

from .a2c import A2C
from . import util

# pylint: disable=R0902
class PPO(A2C):
    """
    Train TensorFlow actor-critic models using PPO.

    This works with any model that implements
    anyrl.models.TFActorCritic.

    For more on PPO, see:
    https://arxiv.org/abs/1707.06347
    """
    def __init__(self,
                 model,
                 epsilon=0.2,
                 **a2c_kwargs):
        self._epsilon = epsilon
        param_shape = (None,) + model.action_dist.param_shape
        self._orig_action_params = tf.placeholder(tf.float32, param_shape)
        super(PPO, self).__init__(model, **a2c_kwargs)

    def _create_objective(self, vf_coeff, entropy_reg):
        actor, critic, mask = self.model.batch_outputs()

        dist = self.model.action_dist
        new_log_probs = dist.log_prob(actor, self._actions)
        old_log_probs = dist.log_prob(self._orig_action_params, self._actions)
        clipped_obj = _clipped_objective(new_log_probs, old_log_probs,
                                         self._advs, self._epsilon)
        critic_error = self._target_vals - critic
        self.actor_loss = util.masked_mean(mask, clipped_obj)
        self.critic_loss = util.masked_mean(mask, tf.square(critic_error))
        self.entropy = util.masked_mean(mask, dist.entropy(actor))
        self.objective = (self.actor_loss + entropy_reg * self.entropy -
                          vf_coeff * self.critic_loss)

    def feed_dict(self, rollouts, batch=None):
        if batch is None:
            batch = next(self.model.batches(rollouts))
        feed_dict = super(PPO, self).feed_dict(rollouts, batch)
        orig_outs = util.select_model_out_from_batch('action_params', rollouts, batch)
        feed_dict[self._orig_action_params] = orig_outs
        return feed_dict

    # pylint: disable=W0221
    def optimize(self, learning_rate=1e-3):
        trainer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        return trainer.minimize(-self.objective)

    def run_optimize(self, optimize_op, rollouts, batch_size=None, num_iter=12):
        """
        Run several steps of training with mini-batches.
        """
        remaining_iter = num_iter
        batches = self.model.batches(rollouts, batch_size=batch_size)
        for batch in batches:
            self.model.session.run(optimize_op, self.feed_dict(rollouts, batch))
            remaining_iter -= 1
            if remaining_iter == 0:
                break

    # TODO: API that supports schedules and runs the
    # entire training loop for us.

def _clipped_objective(new_log_probs, old_log_probs, advs, epsilon):
    """
    Compute the component-wise clipped PPO objective.
    """
    prob_ratio = tf.exp(new_log_probs - old_log_probs)
    clipped_ratio = tf.clip_by_value(prob_ratio, 1-epsilon, 1+epsilon)
    return tf.minimum(advs*clipped_ratio, advs*prob_ratio)
