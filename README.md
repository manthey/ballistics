# Ballistics of Historical Black Powder Tests

This program and data attempts to answer the question of how black powder has varied over time.  The main technique is to gather historical test data and use modern external ballistics to calculate the usefully generated power per unit weight of the gunpowder used in each test.

The main focus is on the 18th century.  One question in particular is how the black powder we purchase today compares with the powder that was produced commercially in the 18th century.

The scope of this research is focused on black powder as a relatively mature technology.  I am not particularly interested in the origin or invention of black powder; rather I'm interested in it as it was when it was a ubiquitous and required substance.

## Process the data

```
mkdir results
python process.py --multi data --out=results
```

Then, to make it available to the web client,

```
mkdir public/data
python utils/combine.py --out=public/data --limit=notrajectory --json
```

## Client setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```
