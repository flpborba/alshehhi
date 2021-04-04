# ALSHEHHI

An implementation of the IND-CCA adaptation of Loidreau's public key encryption scheme presented in Shehhi et al. (see section References.)

# Dependencies

This code's dependencies are listed in `environment.yml` and can be installed using conda:

```
conda env create --file environment.yml
```

As suggested in the `sage` package [installation guide], use `mamba` for a faster dependency solver:

```
conda install -c conda-forge mamba
mamba env create --file environment.yml
```

# References

Shehhi H.A., Bellini E., Borba F., Caullery F., Manzano M., Mateu V. (2019) An IND-CCA-Secure Code-Based Encryption Scheme Using Rank Metric. In: Buchmann J., Nitaj A., Rachidi T. (eds) Progress in Cryptology – AFRICACRYPT 2019. AFRICACRYPT 2019. Lecture Notes in Computer Science, vol 11627. Springer, Cham. https://doi.org/10.1007/978-3-030-23696-0_5

Loidreau, P. (2017). A New Rank Metric Codes Based Encryption Scheme. In: Lange, T., Takagi, T. (eds) Post-Quantum Cryptography . PQCrypto 2017. Lecture Notes in Computer Science(), vol 10346. Springer, Cham. https://doi.org/10.1007/978-3-319-59879-6_1


[installation guide]: https://doc.sagemath.org/html/en/installation/conda.html#sec-installation-conda
