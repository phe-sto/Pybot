# Pybot
This automation framework aims to interact with GUI (web, desktop, etc)or Android. Many tasks
could be automated, like information harvesting or test. Script can be designed with Sikuli IDE.
The framework then convert Sikuli project to python 3 to to take advantage of that powerful scripting language.

## Platforms
  At the moment, for computer, only Windows platforms are supported. Android can be accessed by mirroring thanks to [scrpy](https://github.com/Genymobile/scrcpy) embedded in this framework
  
## Why another framework
  Sikuli IDE is a extremely powerful tool to script automation through any GUI, web browser, android, etc... The only python3 compliant wrapper around Sikuli is lackey.
  This then use lackey and other libraries to be complete the laking feature of Sikuli.
  Unlike pure Sikuli that use JVM and therefore Jython to access some low level API, this framework access platform API via (more) robust python method.
  Other methods are available from the Auto class extract information from the GUI.

## Dependencies
  [Python 3.6](https://www.python.org/downloads/),the lackey and virtualenv pip packages, only python3 Sikuli wrapper.
  Sikuli method name are named like built-in or classical python method like `type()`. lackey renamed the original method an _,
  `type()` becomes `type_()`. For the same reason is also depend on the pip package virtualenv, cause it is highly recommended to run this library out of classical pyrthon.

### Note
  The all purpose is to use to possibility to script GUI element it is much more convient to use an IDE like [Sikuli IDE](http://www.sikuli.org/downloadrc3.html) to initiate scripts.
  Sikuli is java based, therefore you need [Java](https://www.java.com/fr/download/). So they are not dependencies but...

## Contact
  https://PapIT.fr or christophe.brun@papit.fr