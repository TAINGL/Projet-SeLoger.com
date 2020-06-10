"""
A simple streamlit app to predict housing prices
run the app by installing streamlit with pip and typing
> streamlit run seloger_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error


from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet, SGDClassifier
from sklearn.ensemble import GradientBoostingRegressor
import locale

# CHANGER LE CHEMIN D'IMPORTATION DES FICHIERS CSV SELON L'UTILISATEUR
# Import the data (features + labels)
DATA_URL = {
    'Lyon': '/Users/Johanna/Documents/SIMPLON DATA IA/IA/ML PROJET/PROJET SELOGER.COM/csv/csv_int_final/lyon_df.csv',
    'Paris': '/Users/Johanna/Documents/SIMPLON DATA IA/IA/ML PROJET/PROJET SELOGER.COM/csv/csv_int_final/paris_df.csv'
}

# SideBar with features and option 
# Title
st.title("PredictLogement")
st.markdown("L'application qui vous aide à prédire le prix de votre logement au bon prix - par SeLoger.com")

# Image Manipulation
st.image('https://www.strategies.fr/sites/default/files/assets/images/strats-image-1057677.jpeg', width= 800)
# <iframe width="828" height="466" src="https://www.youtube.com/embed/CUlWidhZS04" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


# Permet de garder resultat fonction en cache
@st.cache(allow_output_mutation=True)
# Load data
def get_data(dic, column):
    target = "sl_prix"
    seloger =  pd.read_csv(dic[column], index_col = 0)
    y = np.log(seloger[target])# get labels
    X = seloger.drop(target, axis=1) #
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    return seloger, X_train, X_test, y_train, y_test



# Train the model
def classifiers(classifier):
    classifiers = {
        'Linear Regression': LinearRegression(copy_X=True, fit_intercept=True, n_jobs=None, normalize=False),
        'Lasso': Lasso(alpha=0.001, copy_X=True, fit_intercept=True, max_iter=1000,
                       normalize=False, positive=False, precompute=False, random_state=None,
                       selection='cyclic', tol=0.0001, warm_start=False),
        'Ridge': Ridge(alpha=2, copy_X=True, fit_intercept=True, max_iter=None, normalize=False,
                       random_state=None, solver='auto', tol=0.001),
        'Elastic net': ElasticNet(alpha=0.01, copy_X=True, fit_intercept=True, l1_ratio=0,
                                  max_iter=1000, normalize=False, positive=False, precompute=False,
                                  random_state=None, selection='cyclic', tol=0.0001, warm_start=False), 
        'Ensemble': GradientBoostingRegressor(n_estimators = 400, max_depth = 5, min_samples_split = 2,
                                              learning_rate = 0.1, loss = 'ls')
    }

    classifiers[classifier].fit(X_train, y_train)
    y_pred = classifiers[classifier].predict(X_test)
    return classifiers[classifier], y_pred

# Make predictions
def if_yes_then(name, columns):
    if name == 'Oui':
        seloger[columns] = 1
        return 1
    else:
        seloger[columns] = 0
        return 0

def localisation(name):
    # Split the data
    if name == 'Paris':
        seloger, X_train, X_test, y_train, y_test = get_data(DATA_URL, "Paris")
        return seloger, X_train, X_test, y_train, y_test
    else:
        seloger, X_train, X_test, y_train, y_test = get_data(DATA_URL, "Lyon")
        return seloger, X_train, X_test, y_train, y_test

st.sidebar.subheader("✔️ Prediction du prix de votre logement")
st.sidebar.subheader("Faites varier les features pour connaître le meilleur prix de vente de votre appartement ou maison ")

st.sidebar.title("Ville")                  
Ville = st.sidebar.radio("Localisation du logement", ('Paris', 'Lyon'))
seloger, X_train, X_test, y_train, y_test = localisation(Ville)

def input_data():
    # Critère essentiel du logement
    st.sidebar.title("Quartier")
    if Ville == 'Paris':     
        Localisation = st.sidebar.radio("Localisation du logement", ('Paris 16', 'Autres arrondissements'))
    else: 
        Localisation = st.sidebar.radio("Localisation du logement", ('Lyon 6', 'Autres arrondissements'))
    localisation_logement = {'Autres arrondissements':0, 'Paris 16':1, 'Lyon 6':1 }

    st.sidebar.title("Type du logement")        
    Style = st.sidebar.selectbox("Style", ('Appartement', 'Triplex'))
    style_logement = {'Appartement':0, 'Triplex':1}

    st.sidebar.title("Combien de mètre carré")  
    min_taille = min(seloger['sl_taille'])
    max_taille = max(seloger['sl_taille'])
    Taille = st.sidebar.slider("Taille", min_value= min_taille,  max_value= max_taille)
    st.sidebar.title("Nombre de pièce")
    res_piece = sorted(seloger['sl_nb_piece'].unique())         
    Piece = st.sidebar.selectbox("Nombre de piece",res_piece)
    st.sidebar.title("Nombre de chambre")
    res_chambre = sorted(seloger['sl_nb_chambre'].unique())         
    Chambre = st.sidebar.selectbox("Nombre de chambre",res_chambre)

    # Description du logement
    st.sidebar.title("Logement situé à/au")     
    Etage = st.sidebar.selectbox("Etage", sorted(seloger['sl_etage'].unique()))
    st.sidebar.title("Quel hauteur de logement") 
    Hauteur = st.sidebar.selectbox("Hauteur du logement", sorted(seloger['sl_hauteur'].unique()))
    st.sidebar.title("Année de construction du logement")
    Annee = st.sidebar.selectbox("Annee",('Année de construction 1900', 'Autres'))
    annee_logement = {'Année de construction 1900':1, 'Autres':0}

    st.sidebar.title("Nombre de salle d'eau")  
    Salle_eau = st.sidebar.selectbox("Salle d'eau",sorted(seloger['sl_salle_d_eau'].unique()))
    st.sidebar.title("Nombre de salle de bain")
    Salle_de_bain = st.sidebar.selectbox("Salle de bain",sorted(seloger['sl_salle_de_bain'].unique()))
    st.sidebar.title("Nombre de toilette")     
    Toilette = st.sidebar.selectbox("Toilette",sorted(seloger['sl_toilette'].unique()))
    st.sidebar.title("Type de cuisine?")        
    Cuisine = st.sidebar.selectbox("Cuisine", ('Cuisine séparée équipée', 'Autres'))
    cuisine_logement = {'Cuisine séparée équipée':1, 'Autres':0}


    # Option du logement
    st.sidebar.title("Avec ou sans ascenseur") 
    Ascenseur = st.sidebar.radio("Présence d'un ascenseur", ('Oui', 'Non'))
    ascenseur_logement = if_yes_then(Ascenseur, 'sl_ascenseur')
    st.sidebar.title("Présence d'un parking")   
    Parking = st.sidebar.radio("Présence d'un parking", ('Oui', 'Non'))
    parking_logement = if_yes_then(Parking, 'sl_parking')
    st.sidebar.title("Présence d'une cave?")    
    Cave = st.sidebar.radio("Présence d'une cave", ('Oui', 'Non'))
    cave_logement = if_yes_then(Cave, 'sl_cave')
    st.sidebar.title("Avec ou sans Balcon") 
    Balcon = st.sidebar.radio("Présence d'un balcon", ('Oui', 'Non'))
    balcon_logement = if_yes_then(Balcon, 'sl_balcon')
    st.sidebar.title("Avec ou sans Terrasse") 
    Terrasse = st.sidebar.radio("Présence d'une terrasse?", ('Oui', 'Non'))
    terrasse_logement = if_yes_then(Terrasse, 'sl_terrasse')

    st.sidebar.title("Avec exposition?")        
    Exposition = st.sidebar.selectbox("Avec une exposition",('Orientation Nord-Ouest', 'Autres'))
    exposition_logement = {'Orientation Nord-Ouest':1, 'Autres':0}
    st.sidebar.title("Présence d'une belle vue?") 
    Vue = st.sidebar.radio("Présence d'une belle vue", ('Oui', 'Non'))
    vue_logement = if_yes_then(Vue, 'sl_vue')
    st.sidebar.title("Logement refait à neuf?")          
    Neuf = st.sidebar.radio("Logement refait à neuf?", ('Oui', 'Non'))
    neuf_logement = if_yes_then(Neuf, 'sl_neuf')
    st.sidebar.title("Sol avec parquet")       
    Parquet = st.sidebar.radio("Sol avec parquet", ('Oui', 'Non'))
    parquet_logement = if_yes_then(Parquet, 'sl_parquet')
    st.sidebar.title("Présence d'un gardien?") 
    Gardien = st.sidebar.radio("Présence d'un gardien", ('Oui', 'Non'))
    gardien_logement = if_yes_then(Gardien, 'sl_gardien')
    st.sidebar.title("Choix du modèle de prédiction de prix")
    Model = st.sidebar.selectbox("Modèle", ("Linear Regression", "Lasso", "Ridge", "Elastic net", "Ensemble"))

    #dataframe user
    input_user = np.array([localisation_logement[Localisation],  style_logement[Style], Taille, Piece, Chambre,
                           Etage, Hauteur, annee_logement[Annee], Salle_eau, Salle_de_bain, Toilette, cuisine_logement[Cuisine], 
                           ascenseur_logement, parking_logement, cave_logement, balcon_logement, terrasse_logement, 
                           exposition_logement[Exposition], vue_logement, neuf_logement, parquet_logement, gardien_logement]).reshape(1,-1)

    df_user = pd.DataFrame(input_user, columns = ['sl_localisation','sl_style','sl_taille','sl_nb_piece','sl_nb_chambre',
                                                  'sl_etage','sl_hauteur','sl_annee','sl_salle_d_eau','sl_salle_de_bain','sl_toilette','sl_cuisine',
                                                  'sl_ascenseur', 'sl_parking', 'sl_cave', 'sl_balcon', 'sl_terrasse',
                                                  'sl_exposition','sl_vue', 'sl_neuf', 'sl_parquet', 'sl_gardien']) 

    classifier, y_pred =classifiers(Model)

    return df_user, classifier, Ville, seloger, X_train, X_test, y_train, y_test, y_pred

def RMSE (y_test, y_pred):
    return mean_squared_error(y_test, y_pred)

def modele():
    df_user, classifier, Ville, seloger, X_train, X_test, y_train, y_test, y_pred = input_data()

    seloger, X_train, X_test, y_train, y_test = get_data(DATA_URL, Ville)

   # metrics
    score_rmse = RMSE(y_test, y_pred)

   # display prediction
    predict_prices = classifier.predict(df_user)
    predict_prices = np.exp(predict_prices)
    
    return predict_prices, score_rmse


# Prediction
predict_prices, score_rmse = modele()

#afficher prediction
if st.checkbox('Prediction'):
    #st.subheader('Metrique du modele')
    #st.text("Justesse du modele")
    #st.write(round(score_rmse,2),"%")
    st.subheader("Prix du logement")
    l = locale.setlocale(locale.LC_ALL, '') # avoir le bon currency format
    price = locale.currency(predict_prices[0], grouping=True) 
    st.write("Le prix de vente du logement est estimé à {} €".format(price))
    
