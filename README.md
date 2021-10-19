Dckingdoms is a discord bot written in python to transform your discord
server into a kingdoms server. This bot allows users to create kingdoms
and regions which can then be joined by users of the discord server.
Kings can decide to attack regions that are part of other kingdoms.
Players can train and work every hour to gain strength and workpower.
Strength can be used in a battle by each user to deal damage and
workpower can be used by kings to deal damage. Stock market data is generated
by the simple stock market generator tool: https://github.com/lwaw/simple-stock-market-simulator.

This bot stores discrord user id's of people that participate in the
game. At anytime players can quit the game and the user id will then be
removed from the database.

The following commands are available:

All commands start with "-dck", arguments are separated by a whitespace:
"-dck set_admin @user"

Admin commands:

-   start\_game

-   end\_game

-   create\_kingdom kingdomname

-   create\_region kingdomname regionname

-   set\_admin @user

-   demote\_admin @user

-   set\_king kingdomname @user

King commands:

-   attack\_region kingdomname regionname

-   use\_workpower kingdomname regionname amount

Citizen commands:

-   join\_kingdom kingdomname regionname

-   train

-   work

-   change\_location regionname

-   attack regionname amount

-   defend regionname amount

-   buy\_strength amount

-   leave\_game

** Trading on the stock market has a flat fee of 50 cents and 1 cent per share. **

- buy_stocks company_name amount

- sell_stocks company_name amount

General commands:

-   profile @user

-   kingdom kingdomname

-   kingdom\_list

-   region\_list

-   status\_battle regionname

-   show\_stocks

-   show\_wallet @user

-   github

If you encounter errors or have suggestions, please send an email to
info@fantasy-sim.com.

* * * * *

Version: 1.1

This project is licensed under the terms of the Creative Commons
Attribution-ShareAlike 4.0 International Public License license

Copyright 2021, Laurens Edwards, All rights reserved.

https://github.com/lwaw/dckingdoms

* * * * *
