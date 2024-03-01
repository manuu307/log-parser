# LogParser

## Brief description

> The idea behind this code it's to use it as a framework to create and customize scripts that read and parse log files. you can add your own functionality to generate alerts, reports and more.

## Installation

> For now, this code is not using any library. I used Python 3.11.6 to develop this script and it's working well.
>
> In order to run it, you can just clone this repo and run it by using "python3 run.py" or "python run.py"

## How to use it

> I'm going to start by enumerating the different parts of the framework in order to reach a quick and basic configuration to start running it.
>
> - #### *Folder* **parsers/**: 
>   - Inside this folder you can create different parsers in order to extract the information you need from every log line. There are 3 basic examples that can be youseful to understand this part.
>
> - #### *Folder* **utils/**:
>   - You can create any extra function you can add to the process, for example: sending emails, connection to telegram, regexp patterns to parse log lines and whatever you need.
> - #### *File* **pipelines.py**:
>   - The destiny of this file is to separate the whole process by stages: **open_pipeline**, **middle_pipeline**, **end_pipeline**. You can create your own logic to appply to each of this stages. 
>       - **open_pipeline**: For example the opening of a database conection at the begining or any initial configuration.
>       - **middle_pipeline**: In this case you can for example give format, analyze and/or store every log data returned by the parsers in the database using the previous database connector.
>       - **end_pipeline**: When the process end you can maybe close the database connection, return stats of the process, send an email report, etc.
> - #### *File* **schemas.py**:
>   - This file was made to create the dataclasses or schemes that give format to your log results. Apart from that you can add any schema you need here.
> - #### *File* **config.py**:
>   - In this file you can declare any variable to store data such as: database connection credentials, filters, email service credentials, log file paths, etc.
> - #### *File* **log_parser.py**:
>   - This is the heart of it, in this file it's where the "engine" goes. I think that this file must be left alone unless you really need to change something. The best way to modify the behavior is to use the settings object and set up the best configuration possible to fit your case.
> - #### *File* **run.py**:
>   - In this file there's an example of initial settings and the calling of the main process to start the engine.
