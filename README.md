# RedditTopOfBot
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#Requirements">Requirements</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

So basically we needed a discord bot that fetches the top post of the week from a given subreddit every week. 

While we were programming it, we thought why not make it "potent", which resulted in a fully working, multiserver bot.


### Built With

* [Python 3.9](www.python.org)



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Requirements
You should have already installed python and create a discord bot with the token on hand/ready to paste.


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/IQisMySenpai/RedditTopOfBot.git
   ```
2. Create a token file
   ```sh
   cd 'Your repo location'
   touch secret.py
   nano secret.py
   ```
3. Put your token in following code 'TOKEN = "TOKEN GOES HERE"' then save and exit.
   Example of the content of the secret.py file. Make sure not to add this file to your git, since your token is a secret.
   ```sh
   TOKEN = "KSciUF702bY3brOci1E9BG24Yz0KnBS1jc30aQUw"
   ```



<!-- USAGE EXAMPLES -->
## Usage

For running the bot simply run:
```sh
python3 bot.py
```



<!-- ROADMAP -->
## Roadmap

Maybe if we are bothered we might upgrade to MongoDB instead of saving JSON files but currently we don't a F:D


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- CONTACT -->
## Contact

Project Link: [https://github.com/IQisMySenpai/RedditTopOfBot](https://github.com/IQisMySenpai/RedditTopOfBot)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Did 50% of the coding with 'Code with me' in PyCharm
* [Alisot2000](https://github.com/AliSot2000)

