import tensorflow as tf
from utils import normalize

### LOSS FUNCTIONS

def cde_loss(beta, z_basis, shrink_factor, name="cde_loss"):
    with tf.name_scope(name):
        complexity_terms = tf.reduce_sum(tf.square(beta), axis=1) + 1.0
        fit_terms = tf.reduce_sum(tf.multiply(beta, z_basis), axis=1) + 1.0
        loss = tf.reduce_mean(complexity_terms - 2 * fit_terms) / shrink_factor
        return loss

def nll_loss(beta, z_basis, shrink_factor, name="nll_loss"):
    with tf.name_scope(name):
        fit_terms = tf.reduce_sum(tf.multiply(beta, z_basis), axis=1) + 1.0
        loss = tf.reduce_mean(-fit_terms) / shrink_factor
        return loss


### EXTRA LAYER (before softmax)

def cde_layer(inputs, weight_sd, marginal_beta, name="cde_layer"):
    with tf.name_scope(name):
        W_shape = [int(inputs.shape[1]), len(marginal_beta) - 1]
        W = tf.Variable(tf.random_normal(W_shape, stddev=weight_sd), name="W")
        b = tf.get_variable("b", initializer=marginal_beta[1:])
        beta = tf.matmul(inputs, W) + b
        # tf.summary.histogram("weights", W)
        # tf.summary.histogram("biases", b)
        # tf.summary.histogram("betas", beta)
        return beta


### PREDICTION FUNCTION

def cde_predict(sess, beta, z_min, z_max, z_grid, z_grid_basis, input_dict):
    beta = sess.run(beta, feed_dict=input_dict)
    n_obs = beta.shape[0]
    beta = np.hstack((np.ones((n_obs, 1)), beta))
    cdes = np.matmul(beta, z_grid_basis.T)
    normalize(cdes)
    cdes /= np.prod(z_max - z_min)
    return cdes