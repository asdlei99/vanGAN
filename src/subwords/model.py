import torch
import torch.nn as nn
import torch.nn.functional as F
# from properties import *


class Generator(nn.Module):
    def __init__(self, input_size, output_size, hidden_size):
        super(Generator, self).__init__()

        self.map1 = nn.Linear(input_size, output_size, bias=False)
        #nn.init.orthogonal(self.map1.weight)
        nn.init.eye_(self.map1.weight.data)   # As per the fb implementation initialization

    def forward(self, x):
        return self.map1(x)

    def save(self, filename):
        torch.save(self.state_dict(), filename)

    def load(self, filename):
        map_location = 'gpu' if self.map1.weight.is_cuda else 'cpu'
        self.load_state_dict(torch.load(filename, map_location=map_location))

class Discriminator(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, hyperparams):
        dropout_inp = hyperparams.dropout_inp
        dropout_hidden = hyperparams.dropout_hidden
        leaky_slope = hyperparams.leaky_slope
        self.add_noise = hyperparams.add_noise
        self.noise_mean = hyperparams.noise_mean
        self.noise_var = hyperparams.noise_var

        super(Discriminator, self).__init__()
        self.map1 = nn.Linear(input_size, hidden_size)
        self.drop1 = nn.Dropout(dropout_inp)
        self.activation1 = nn.LeakyReLU(leaky_slope)
        self.map2 = nn.Linear(hidden_size, hidden_size)
        self.drop2 = nn.Dropout(dropout_hidden)    # As per the fb implementation
        self.activation2 = nn.LeakyReLU(leaky_slope)
        self.map3 = nn.Linear(hidden_size, output_size)

    def gaussian(self, ins, mean, stddev):
        noise = torch.autograd.Variable(ins.data.new(ins.size()).normal_(mean, stddev))
        return ins * noise

    def forward(self, x):
        if self.add_noise:
            x = self.gaussian(x, mean=self.noise_mean, stddev=self.noise_var)  # muliplicative guassian noise
        x = self.activation1(self.map1(self.drop1(x))) # Input dropout
        x = self.drop2(self.activation2(self.map2(x)))
        return F.sigmoid(self.map3(x)).view(-1)

    # def parameters(self):
    #     """Returns model parameters that require gradients."""
    #     return filter(lambda p: not p.requires_grad,
    #                   super(Discriminator, self).parameters())
