# heart_rate_sentinel_server
[![Build Status](https://travis-ci.com/AznStevy/heart_rate_sentinel_server.svg?branch=master)](https://travis-ci.com/AznStevy/heart_rate_sentinel_server)

The heart rate sentinel server is meant to be a primer into web infrastructure. Here, `flask` is used to handle most of the backend routing. The server currently uses a sandbox mlab mongo database to store data. You can accessed the deployed version using a command like the following:
```
http://vcm-7308.vm.duke.edu:5000/api/heart_rate/LFYXEBJKHY
```

## Configuration
The `config.json` file is mostly used for the Sendgrid API. The structure should be as follows, where `SENDGRID_API_KEY` is your key, and `from_email` is the email you wish to send from. You must also provide mongo credentials in order to allow the app to access the database. These are submitted on Sakai... they are also committed in `config.json` because the data isn't real...
```
{
    "SENDGRID_API_KEY": "",
    "from_email": "",
    "mongo_user": "",
    "mongo_pass": "",
}
```

## Environment Set-up
To set up the environment, you first need to set up a virtual environment using `python3 -m venv env
` in the project folder (if you're on linux). Then use `pip install -r requirements.txt`. If you don't have pip, then you should do `sudo apt-get update` and `sudo apt-get -y upgrade` to update packages and then do `sudo apt-get install python-pip` to isntall pip. This was only tested with python 3.6 so far.

## Run web server
To run the `flask` web server, it's best to do so on a screen. The most painless way is to do:
```
screen -S test -d -m python heart_rate_sentinel_server.py
```
which creates the screen and then immediately detaches it. You may need to use `python3` instead if python is python2 by default on the system.

## HRDatabase
The project was first done by storing everything in RAM, getting that to work, and then moving on to a mongo implementation. Thus, the goal of this class was to be as least intrusive to existing code as possible. The structure of each entry contains the 5 attributes that were designated in the assignment. The  `HRDatabase` class contains typical functions that allow for simple addition, removal, and search of patients. No test functions were implemented for this because I was told we didn't need it.

## Heart Rate API
The heart rate API is contained in `hr_api.py`. If it is directly run using `python hr_api.py`, it will go through a simulated usage of the API. That code is reproduced below:
```python
    from random import choice
    from string import ascii_uppercase

    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    print(p_id)
    r = add_new_patient(p_id, "szx2@duke.edu", 21)
    print(r, get_all_patients())
    r = post_heart_rate(p_id, 80)
    print("Posted: ", r)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)
    r = post_heart_rate(p_id, 90)
    print("Posted: ", r)
    av = get_heart_rate_average(p_id)
    print("Average: ", av)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)

    curr_status, timestamp = get_patient_status(p_id)
    print("Current Status 1 (False/Not Tach): ", curr_status, "Timestamp: ", timestamp)
    int_avg = get_interval_average(p_id, timestamp)
    print("Interval Average (should be 85):", int_avg)

    r = post_heart_rate(p_id, 100)
    print("Posted: ", r)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)
    r = post_heart_rate(p_id, 110)

    curr_status, _ = get_patient_status(p_id)
    print("Current Status 2 (True/Tach + sends email): ", curr_status, "Timestamp: ", timestamp)
    av = get_heart_rate_average(p_id)
    print("Average (95): ", av)
    int_avg = get_interval_average(p_id, timestamp)
    print("Interval Average (should be 85):", int_avg)
```