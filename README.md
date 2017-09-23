# anyrl-py

This is a Python remake (and makeover) of [anyrl](https://github.com/unixpickle/anyrl). It is a general-purpose library for Reinforcement Learning which aims to be as modular as possible.

# APIs

There are several different sub-modules in anyrl:

 * `models`: abstractions and concrete implementations of RL models. This includes actor-critic RNNs, MLPs, CNNs, etc. Takes care of sequence padding, BPTT, etc.
 * `rollouts`: APIs for gathering and manipulating batches of episodes or partial episodes. Many RL algorithms include a "gather trajectories" step, and this sub-module fulfills that role.
 * `algos`: well-known learning algorithms like policy gradients or PPO. Also includes mini-algorithms like Generalized Advantage Estimation.
 * `dists`: parameterized probability distributions. Makes it easy to implement stochastic policies.

# Motivation

Currently, most RL code out there is very restricted and not properly decoupled. In contrast, anyrl aims to be extremely modular and flexible. The goal is to decouple agents, learning algorithms, trajectories, and things like GAE.

For example, anyrl decouples rollouts from the learning algorithm (when possible). This way, you can gather rollouts in several different ways and still feed the results into one learning algorithm. Further, and more obviously, you don't have to rewrite rollout code for every new RL algorithm you implement. However, algorithms like A3C and Evolution Strategies may have specific ways of performing rollouts that can't rely on the rollout API.

# Use of TensorFlow

This project relies on TensorFlow for models and training algorithms. However, anyrl APIs are framework-agnostic when possible. For example, the rollout API can be used with any policy, whether it's a TensorFlow neural network or a native-Python decision forest.

# TODO

Here is the current TODO list, organized by sub-module:

* `models`
  * CNN models
  * Unshared actor-critics for TRPO and the like.
  * Vectorizers:
    * Combine vectorizers with distributions.
* `rollouts`
  * Maybe: way to not record states in `model_outs` (memory saving)
* `algos`
  * TRPO
* `dists`
  * Bernoulli
  * MultiBinary
  * Tuple
  * Gaussian
  * Tests for all distributions.
