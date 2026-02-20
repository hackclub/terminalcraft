# CommandLine Web Browser
A simple command-line web browser, written in Java, using Lanterna and Jsoup.\
Most web pages can be read in a simplistic state, though Cloudflare seems to block access to some pages.
The interface has a traditional browser toolbar at the top, with forward and back arrows, etc.
![example](https://www.wiicart.net/img/clbrowser.png)

# How To Run
Download the JAR file locally, which can be found [here](https://github.com/Wiicart/CommandLineWebBrowser/releases), 
[here](https://www.wiicart.net/clbrowser/clbrowser-1.0.jar), or in this directory.
 - Example Command: `curl -L -O -A "Mozilla/5.0" https://www.wiicart.net/clbrowser/clbrowser-1.0.jar`
 - On Linux or Mac, run `java -jar <path-to-clbrowser-1.0.jar>`. If using windows, use `javaw`.

The program relies on the Lanterna, Jsoup and Jfiglet libraries, but they are shaded into the JAR, so no action is needed.

# Why
I created this because when I'm ssh-ing into servers of mine, I usually have a browser open in the next window for references.
I figured a program like this could be useful for quickly glancing at a webpage without having to switch windows.