# ---------------------------------------------------------------#
#   astroNN.nn.metrics: metrics
# ---------------------------------------------------------------#

from astroNN.nn.losses import mean_absolute_error
from astroNN.nn.losses import mean_absolute_percentage_error
from astroNN.nn.losses import mean_squared_error
from astroNN.nn.losses import mean_squared_logarithmic_error
from astroNN.nn.losses import categorical_accuracy
from astroNN.nn.losses import binary_accuracy


# Just alias functions
mse = mean_squared_error
mae = mean_absolute_error
mape = mean_absolute_percentage_error
msle = mean_squared_logarithmic_error
