# usaa_csv_to_ofx
Way to get around USAA disabling their ofx downloads

USAA, the bank, decided to drop support for downloading OFX files of all of your account transactions, and only allows
you to either pay Quicken $45+ a year for them to sell your most-sensitive marketing data, or, download a csv for each
account that is really pretty terrible(no transaction ids, no account ids, almost just the payee, the date, and the
amount.)

After jabbering with their Customer Service drones in their community site for two weeks, I finally said enough,
and wrote a workaround.

NOTE:
THIS IS NOT SUPPORTED IN ANY WAY OR PRODUCTIZED.
THIS IS JUST A BIG EFF YOU TO USAA FOR REMOVING A BASIC FEATURE OF ANY BANK AND TO HOPEFULLY SAVE SOMEONE SOME
TIME IF THEY KNOW WHAT TO DO WITH THIS.
THIS IS HACKY AF.
THIS IS NOT PRETTY CODE.

This is just a standalone block of code that uses OfxParse(0.16 I think.  There's a newer version than what I'm using
available though https://github.com/jseutter/ofxparse) and
Arrow (https://arrow.readthedocs.io/en/latest/) libraries, and is built on Python 2.7.

It assumes a file structure like:
working dir/
    MAY_2020/
        your_checking/
            bk_download.csv
        your_savings/
            bk_download.csv
    APRIL_2020/
    account_maps.csv

Right now, it dumps everything out to an ofx file named testing.ofx in the working directory.
To support my workflow, you can pass it one parameter, "-d MAY_2020" or "-d APRIL_2020" or whatever the heck you want
to name your monthly/whatever period of directories, to tell it what directory to look in.
Just edit the account_maps.csv file with your account id for each type of account(do NOT upload this anywhere,
seriously) and whatever directories you would like to dump each account's csv file into, to keep the association
so it can put the right account id with the right transactions in your ofx file.
Download each account's monthly/whatever csv into the appropriate account's directory, and then fire it off with
the -d parameter for your first-level dir, and it will drop an ofx file in your current working directory.

If you're trying to make this work with Microsoft Money or something else, it may care a lot more about the various
ids and such.  I just need account to transaciton and date, and unique transaction ids, so that's all I did.

USAA basically has some unique counter per account per id per day that it uses in its exporter for transaction id,
so I made some gross assumptions about it and just increment the ids each day.

Use at your own risks.