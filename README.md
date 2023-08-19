# SplendorRL: A Reinforcement Learning Environment for Splendor

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
<!-- - [![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) -->

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Notice](#notice)
<!-- - [Documentation](#documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information) -->

## Project Description

**SplendorRL** is a personal passion project that is intended to develop intermediate to advanced Python concepts, design patterns, and training of reinforcement learning agents as skills in the context of the popular board game Splendor. The project was born from a desire to explore the effectiveness of different strategies in the game and possibly discovering the optimal strategy by some of the agents trained. From first-hand experience it seemed that luck played a more significant factor than skill, as most times when I played the game, the strategies of the winners didn't appear to follow a clear pattern that was superior to the strategies of the other players.

The primary aim of SplendorRL is to understand and potentially optimize gameplay strategies through the use of agents. In order to create an environment that can be utilized by these agents, the mechanics of the Splendor board game (explained [here](https://www.ultraboardgames.com/splendor/game-rules.php)) had to be written from scratch. Additionally an interface for both human players and agents had to be developed.

**Key Features:**
- [x] Faithful recreation of the Splendor board game mechanics.
- [x] Customizable game parameters to allow for flexible game conditions.
- [x] CLI (Command Line Interface) for human interaction with game mechanics.
- [] CLI (Command Line Interface) for observing agent actions.
- [] Integration with the [PettingZoo framework](https://pettingzoo.farama.org/) for a multi-agent environment.
- [] Training and comparison of different RL algorithms.
- [] GUI (Graphical User Interface) for both humans and agents as players in a game environment.


## Installation

Choose one of the following methods to install and set up SplendorRL on your system:

### Using `venv` and `requirements.txt`

1. Clone the repository:
   ```bash
   git clone https://github.com/Nikola995/Splendor-AI.git
   cd splendor-rl
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Using `conda` and `environment.yml`

1. Clone the repository:
   ```bash
   git clone https://github.com/Nikola995/Splendor-AI.git
   cd splendor-rl
   ```

2. Create a new conda environment from the provided `environment.yml` file:
   ```bash
   conda env create -f environment.yml
   ```

3. Activate the new environment:
   ```bash
   conda activate splendor
   ```

Both methods will set up the necessary environment and dependencies for SplendorRL.

<!-- For detailed installation instructions and troubleshooting, consult the [Installation Guide](./docs/installation.md). -->

## Usage

Currently the only way to interact with the project is by using the command-line interface (CLI). To engage with the simulation environment, follow these steps:

1. Open a terminal window and navigate to the main directory of the project.

2. Run the Python script `splendor_cli.py` using the following command:
   
   ```bash
   python splendor_cli.py

<!-- Discover how to interact with and leverage the SplendorRL environment by exploring diverse usage scenarios and practical examples. To begin, follow these steps:

1. Initialize an RL agent using your preferred library (e.g., TensorFlow, PyTorch).
2. Configure agent and environment settings.
3. Train the agent, utilizing SplendorRL as the training environment.
4. Monitor the agent's progress and strategy refinement.
5. Evaluate the agent's performance against predefined benchmarks.

For comprehensive instructions and code snippets, refer to the [Usage Guide](./docs/usage.md).

## Documentation

In-depth documentation for SplendorRL, encompassing detailed class explanations, function references, and API documentation, can be accessed through the [Documentation Portal](https://yourusername.github.io/splendor-rl-docs/).

## Examples

Explore practical examples showcasing how to effectively employ SplendorRL to train and assess RL agents across a spectrum of Splendor scenarios. Navigate to the [Examples Directory](./examples) for hands-on code samples and guidelines.

## Contributing

We warmly welcome contributions aimed at enhancing SplendorRL and broadening its capabilities. For contribution guidelines, please consult the [Contributing Guide](./CONTRIBUTING.md).

## License

This project operates under the terms of the [MIT License](./LICENSE). -->

## Notice

This implementation of the board game Splendor, known as **SplendorRL**, is primarily a personal learning project.

Please note the following:

- **Educational Use**: SplendorRL is not intended for commercial use or distribution. It is intended for educational purposes only.

- **Official Game**: To experience the full and immersive gameplay of Splendor, I encourage you to support the original creators by purchasing the official game.

- **Acknowledgment**: I deeply appreciate the creativity and effort invested by the designer Marc André and illustrator Pascal Quidault. Their game has inspired this project and serves as a foundation for learning and exploration.

For more information about the original Splendor board game, please visit the [Official Splendor Website](https://www.spacecowboys.fr/splendor-english).



<!-- ## Contact Information

If you have inquiries, feedback, or are interested in collaboration, please feel free to reach out to [Your Name](mailto:your@email.com). -->