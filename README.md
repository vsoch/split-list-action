# Even Hash Action

This is a highly specific action that is intended to help with breaking up data
into different sections. The use case is that you have potentially hundreds or
thousands of string identifiers (e.g., Singularity Registry HPC "shpc" container identifiers)
and you want to run some regular automation across the entire set. Given a few hundred,
you can likely to do this in one action run. However, given over 8K, you need
to more intelligently break up the identifiers into logical sections, and run
a set of updates over a month (e.g., one letter over 26 days). This action will:

 - Take in a list of identifiers, hash them
 - Optionally do more filters, with some custom fitlers (e.g., letter selection or calendar selection)
 - Save the output to file or write to the screen.
 
And that's it! It is a bit customized to the shpc use case, but likely will
have other use cases.

## Usage

Let's say we want to split the entire list of shpc containers into smaller sets,
and ask to run one per day. We'd want a daily workflow that looks like this:

```yaml
name: 'Update Containers'

on:
  schedule:
    # Now daily for a smaller subset of containers
    - cron: '0 17 * * *'

jobs:
  auto-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: '0'

      - name: Install shpc
        run: |
          pip install git+https://github.com/singularityhub/singularity-hpc@main
          
          # Remove default remote registry and add PWD
          shpc config remove registry https://github.com/singularityhub/shpc-registry
          shpc config add registry $(pwd)
          shpc show > listing.txt

      # Run a specific letter matched to a day of the month A==1, Z==26
      - name: Calendar Updater
        uses: vsoch/split-list-action@main
        with:
          ids_file: listing.txt
          outfile: shpc-show-subset.txt

          # One letter assigned to each day
          calendar_split: true

      - name: Run Update on Subset
        run: |
            for entry in $(cat ./shpc-show-subset.txt); do
                shpc update ${entry}
            done
```
