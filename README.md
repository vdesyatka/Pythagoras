<div align="center">
  <img src="http://vlpavlov.org/Pythagoras-Logo3.svg"><br>
</div>

# Pythagoras

### What Is It?

An experimental framework containing advanced Python tools for Data Scientists and ML/AI Engineers. 
Pythagoras is going through a major overhaul now, come back later for updates about new functionality.

### How To Get It?

The source code is hosted on GitHub at:
[https://github.com/vladlpavlov/pythagoras](https://github.com/vladlpavlov/pythagoras) 

Binary installers for the latest released version are available at the Python package index at:
[https://pypi.org/project/pythagoras](https://pypi.org/project/pythagoras)

        pip install pythagoras


### Major Components

* **FileDirDict**, **S3_Dict**, and **ImmutableS3_LocallyCached_Dict**: Persistent storage objects 
with Dict-like interfaces

* **PHashAddress**: A globally unique address of an immutable value. 
Consists of a human-readable prefix and a hash code

### Legacy Components (will be deprecated in H1-2022)

* **LoggableObject**: Base class that provides logging-enabled granular story-telling tools.

* **PickleCache**: Pandas-compatible persistent caching, extendable to work with new classes.

### Tutorials

1. [File-based persistent dictionaries](https://github.com/vladlpavlov/pythagoras/blob/master/pythagoras_FileDirDict_tutorial.ipynb): 
Dictionaries that keep their stated between sessions by stroring key-value pairs as local files.

### Legacy Tutorials

1. [Basic Caching](https://github.com/vladlpavlov/pythagoras/blob/master/pythagoras_caching_introductory_tutorial.ipynb): 
How to speed up your scripts and notebooks if your Python code works with Pandas and build-in datatypes
2. [Advanced Caching](https://github.com/vladlpavlov/pythagoras/blob/master/pythagoras_caching_advanced_tutorial.ipynb): 
How to make pythagoras PickleCache work with custom classes 


### Dependencies

* [pandas](https://pandas.pydata.org/)
* [scikit-learn](https://scikit-learn.org/) 
* [numpy](https://numpy.org/)
* [scipy](https://www.scipy.org/)
* [psutil](https://pypi.org/project/psutil/)

### Key Contacts

* [Volodymyr (Vlad) Pavlov](https://www.linkedin.com/in/vlpavlov/): algorithm design and core development 
* [Kai Zhao](https://www.linkedin.com/in/kaimzhao/): quality assurance

### What Do The Name And Logo Mean?

Pythagoras was a famous ancient Greek thinker and scientist 
who was the first man to call himself a philosopher ("lover of wisdom"). 
He is most recognised for his many mathematical findings, 
including the Pythagorean theorem. 

But not everyone knows that in antiquity, Pythagoras was also credited with major astronomical discoveries,
such as sphericity of the Earth and the identity of the morning and evening stars as the planet Venus. 
Our logo depicts these, lesser known but not less important achievements of Pythagoras.