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
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#hosting">hosting</a></li>
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
You should already have installed python and create a discord bot with the token on hand/ready to paste. A MongoDB database is also required.

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
3. Put in your:
   token, db username, db password, db name, queue collection name, server collection name
   Then save and exit.
   Example of the content of the secret.py file. Make sure not to add this file to your git, since your token etc. is a secret.
   ```sh
   TOKEN = "KSciUF702bY3brOci1E9BG24Yz0KnBS1jc30aQUw"
   db_username = "bot_user"
   db_password = r"dZnep2emk6Sin7PMAj2Hfrb27zFvyw"
   db_name = "TopOfBot"
   col_queue = "queue"
   col_servers = "servers"

   ```

### Hosting
We are using MongoDB Atlas for hosting the db. If you are hosting it yourself you might need to change the client link in mongo_api.

Heroku is our current host for the bot. You will need to generate a Procfile for controlling the bot.py


<!-- USAGE EXAMPLES -->
## Usage

For running the bot simply run:
```sh
python3 bot.py
```

Commands for RedditTopOf:
- changePrefix *[prefix]*\
  Changes the prefix that is used in front of command.\
  *[prefix]* can be any text/character
- getImage *[subreddit] [topOfTime]*\
  Fetches the top post of the given time span\
  *[subreddit]* is the subreddit you want. Can be r/name or just name.\
  *[topOfTime]* needs to be one of ('hour', 'day', 'week', 'month', 'year', 'all').
- addInterval *[subreddit] [topOfTime] [hours] [startTime]*\
  Fetches the top post of the given time span every given hour\
  *[subreddit]* is the subreddit you want. Can be r/name or just name.\
  *[topOfTime]* needs to be one of ('hour', 'day', 'week', 'month', 'year', 'all').\
  *[hours]* how long the bot waits before sending another post. Minimum is 0.25.\
  *[startTime]* (optional) starts the Interval at a given time hh:mm. 24h format; Zero-padded (02:05); 24:00 is invalid.
- listIntervals\
  Lists all your Intervals
- deleteInterval *[name]*\
  Deletes a interval of guild\
  *[name]* of Interval (or * for all)
- help\
  Prints Commands
- fuckYou\
  Insult the bot for a funny reaction
- version\
  Prints Version

<!-- ROADMAP -->
## Roadmap

Maybe if we are bothered we might integrate timezones, but currently we don't a F, since everything works:D


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
Developer Server Link: [https://discord.gg/UAxANEUfhN](https://discord.gg/UAxANEUfhN)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Did 50% of the coding with 'Code with me' in PyCharm
* [Alisot2000](https://github.com/AliSot2000)

