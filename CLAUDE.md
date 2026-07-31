<!-- batallion:init -->
## Batallion

This project uses [batallion](https://github.com/stevencarpenter/batallion) for
autonomous agent campaigns. Quick reference:

```bash
  batallion plan     .batallion/starter.spec.toml    # preview the demo battle plan
  batallion campaign .batallion/starter.spec.toml    # run the demo end-to-end
  batallion brief "<your idea>"    # turn an idea into a spec and run it
  batallion doctrine               # print the active doctrine
  batallion roles                  # list all roles and their charters
  batallion doctor                 # check install + config health
```

Doctrine lives in `.batallion/doctrine/`. Specs live in `.batallion/`.
Campaign artifacts (journals, run outputs) land in `.artifacts/` (gitignored).
