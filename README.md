# Get the menu plan from the ETH and UZH canteens

This is a simple script to get the menu plan from the ETH and UZH canteens.

## Usage
In order to get the lunch menu plan for the ETH and UZH, run the following command:
```bash
python main.py
```

In order to get the dinner menu plan for the ETH and UZH, run the following command:
```bash
python main.py --time abend
```

## Send the menu plan to a signal group
In order to send the menu plan to a signal group, you need to have the signal-cli installed and setup.
After that, define a `secrets.sh` file in the root directory of the project with the following content:

```bash
export SIGNAL_NUMBER="your_signal_number"
export SIGNAL_GROUP="the_id_of_the_group_to_send_the_message_to"
```
Afterwards you can run the following command to send the menu plan to the signal group:
```bash
make mittag_signal
```

or to send the dinner menu plan to the signal group:
```bash
make abend_signal
```

## Adding more mensas
In order to add a new Mensa, you need to add the name to the [MensaNames](src/constants.py) and add 
the corresponding url to the [MensaURL](src/constants.py). After that, you need to add a it to the 
[get_menus()](src/scraping.py) function.