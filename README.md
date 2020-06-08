# Projet-SeLoger.com

Prediction de Prix des logements sur le site SeLoger.com

## Getting Started
### Prerequisites

What things you need to install the software and how to install them

```
fake-useragent==0.1.11
matplotlib==3.1.1
numpy==1.16.4
plotly==4.1.0
regex==2020.2.20
requests==2.22.0
scikit-learn==0.22.2.post1
scipy==1.3.0
streamlit==0.58.0
seaborn==0.9.0
selenium==3.141.0
urllib3==1.25.3
```

### Installing

```
```

## Running the tests

### Scrapping

Pour se faire, n'oublier pas d'indiquer le bon url: ligne 351 et bien nommé vos fichiers: ligne 417, 418

Le script permet d'aller sur les pages du site SeLoger.com, et d'aller sur deux types d'annonce:
- SeLoger.com
<img src="https://github.com/TAINGL/Projet-SeLoger.com/blob/master/img/SeLoger_Annonce.png" width="300"/>

- Belle Demeure
<img src="https://github.com/TAINGL/Projet-SeLoger.com/blob/master/img/BD_Annonce.png" width="300"/>

### Application Streamlit

<img src="https://github.com/TAINGL/Projet-SeLoger.com/blob/master/img/PredictLogement.png" width="300"/>

Take `csv_int_final`and change path line 24.
Run the app by installing streamlit with pip and typing
```
streamlit run seloger_app.py
```

## Authors

* **Laura TAING** - *Scrapping - Préprocessing - Application*  
* **Bintou KOITA** - *Scrapping - Préprocessing - Model* 
* **Nicolas ZYSERMANN** - *Scrapping - Application* - 
* **Ludovic SANNE** - *Scrapping - Préprocessing - Model - Application*
