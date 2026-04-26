## How to connect

First make sure the raspberry pi is turned on.

Join the wifi network group3_autonomous_systems, use the password as described in the groupchat.
This will disable internet access for your laptop if not connected via ethernet.

> Note: it might take a minute or two for the wifi network to come online.

After connecting to the wifi network, we must connect to the raspberry's terminal; we do this via ssh.
Run the following in the terminal of your laptop:

```zsh
ssh group3@as-pi.local
```

> Note: first time when connecting you might need to give your computer access to connect to a remote server.

You will be asked for a password, use the same password as used earlier. 

This should show in your terminal: __group3@as-pi:~ $__
You are now using the terminal of the raspberry pi.

## How to find the right files

Next we must change the working directory to that of our project files.
We do that by using the change directory command followed by the directory

```zsh
cd files/autonomous_systems
```

Your terminal should now show: __group3@as-pi:~/autonomous_systems $__

To list the contents of the current directory, you may use the ls command

```zsh
ls
```

## How to activate the virtual environment

We are using a virtual environment, which allows for modules to be installed in just the environment.
Thus to use the modules we are using in our code, we must activate the virtual environment first.
Use the following terminal command.

```zsh
source env/bin/activate
```

Your terminal should now show: (env) __group3@as-pi:~/autonomous_systems $__

## How to run something
Since we are using python, we use the python command, followed by the filename.
As an example we will use test_robot.py. 
Other scripts can be found through using the ls command.

```zsh
python test_robot.py
```

The program should now run.

> Make sure to __always__ shut down the program by using `control` + `C`

## How to turn off the raspberry pi

Run the shutdown command as described below

```zsh
sudo shutdown now
```

## How to disconnect with the raspberry pi

Type exit to stop the ssh connection.

```zsh
exit
```
