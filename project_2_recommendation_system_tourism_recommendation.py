# -*- coding: utf-8 -*-
"""Project 2 - Recommendation System - Tourism Recommendation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qklWwzkWINDw7HX28_NtJk9sHnjCLWh7
"""

#import library
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""# **DATA UNDERSTANDING**

DATASET : https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination
"""

#load dataset
package = pd.read_csv('/content/drive/MyDrive/dataset/archive (21)/package_tourism.csv')
tourism = pd.read_csv('/content/drive/MyDrive/dataset/archive (21)/tourism_with_id.csv')
rating = pd.read_csv('/content/drive/MyDrive/dataset/archive (21)/tourism_rating.csv')
user = pd.read_csv('/content/drive/MyDrive/dataset/archive (21)/user.csv')

#melihat banyak data
print('Jumlah paket wisata turis : ', len(package.Package.unique()))
print('Jumlah tempat wisata turis : ', len(tourism.Place_Id.unique()))
print('Jumlah rating dari turis : ', len(rating.User_Id.unique()))
print('Jumlah user yang membuat fitur dari user : ', len(user.User_Id.unique()))

tourism

rating

"""# **DATA PREPROCESSING**"""

tourism.info()

"""Jumlah fitur numerik dan kategori pada tourism, diperoleh informasi numerik terdiri dari 8 fitur, dan kategori terdiri dari 5 fitur, diantaranya sebagai berikut :
  - Numerik :
    - Place_Id : int64
    - Price : int64
    - Rating : float64
    - Time_Minutes : float64
    - Lat : float64
    - Long : float64
    - Unnamed: 11 : float64
    - Unnamed: 12 : float 64
  - Kategori :
    - Place_Name : object
    - Description : object
    - Category : object
    - City : object
    - Coordinate : object

Deskripsi variabel sebagai berikut :
    
  *   Place_Id : Id tempat wisata
  *   Place_Name : Nama tempat wisata
  *   Description : Deskripsi tempat wisata
  *   Category : Kategori tempat wisata
  *   City : Kota tempat wisata berada
  *   Price : Harga tempat wisata
  *   Rating : Rating tempat wisata
  *   Time_Minutes : Lama waktu berwisata
  *   Coordinate : Koordinat tempat wisata
  *   Lat : Latitude tempat wisata
  *   Long : Panjang dari tempat wisata
  *   Unamed: 11 : Data tanpa penjelasan
  *   Unamed: 12 : Data tanpa penjelasan 
"""

#drop fitur yang tidak digunakan
tourism = tourism.drop(['Description', 'City', 'Price', 'Rating', 'Time_Minutes', 'Coordinate', 'Lat', 'Long', 'Unnamed: 11', 'Unnamed: 12'], axis = 1)

tourism

rating.info()

"""Jumlah fitur numerik dan kategori pada rating, diperoleh informasi numerik 3 fitur sedangkan kategori tidak ada, diantaranya sebagai berikut :
- Numerik :
  -  User_Id : int64
  -  Place_Id : int64
  -  Place_Ratings : int64

Deskripsi variabel sebagai berikut :
   *   User_Id : Id wisatawan atau turis
   *   Place_Id : Id tempat wisata
   *   Place_Ratings : Rating tempat wisata
"""

rating.describe()

"""Terlihat pada tabel distribusi, dapat dipastikan tidak terdapat bahwa terdapat data duplikat pada fitur User_Id, data duplikat ini akan diproses pada proses data preparation."""

#menggabungkan fitur Category pada tourism ke dalam variabel rating.
all_tourism_name = pd.merge(rating, tourism[['Place_Id', 'Category']], on = 'Place_Id', how = 'left')
all_tourism_name

#menggabungkan fitur Place_Name pada tourism ke dalam variabel rating.
all_tourism = pd.merge(all_tourism_name, tourism[['Place_Id', 'Place_Name']], on = 'Place_Id', how = 'left')
all_tourism

all_tourism.info()

"""Terlihat sekarang variabel all_tourism memiliki 4 data"""

all_tourism.isnull().sum()

"""# **UNIVARIATE EXPLORATORY DATA ANALYSIS**"""

count = all_tourism['Place_Ratings'].value_counts()
percent = 100 * all_tourism['Place_Ratings'].value_counts(normalize = True)
df = pd.DataFrame({'Jumlah sample' : count, 'Persentase' : percent.round(1)})
print(df)
sns.countplot(x = all_tourism['Place_Ratings'], data = all_tourism, palette = 'gist_rainbow', order = all_tourism['Place_Ratings'].value_counts().index)

"""Dapat dilihat pada visualisasi diatas, masing-masing rating memiliki persentase yang hampir mirip, berikut merupakan persentase dan jumlah sample secara spesifik dari visualisasi diatas diurutkan dari yang terbanyak hingga terendah :
  - Rating 4 : 2106 sample, 21.1%
  - Rating 3 : 2096 sample, 21.0%
  - Rating 2 : 2071 sample, 20.7%
  - Rating 5 : 2021 sample, 20.2%
  - Rating 1 : 1706 sample, 17.1%
"""

count = all_tourism['Category'].value_counts()
percent = 100 * all_tourism['Category'].value_counts(normalize = True)
df = pd.DataFrame({'Jumlah sample' : count, 'Persentase' : percent.round(1)})
print(df)
plt.figure(figsize = (10,5))
sns.countplot(x = all_tourism['Category'], data = all_tourism, palette = 'gist_rainbow', order = all_tourism['Category'].value_counts().index)

"""Terlihat bahwa 50% dari keseluruhan data berada pada Category Taman Hiburan dan Budaya, berikut merupakan presentase dan jumlah sample spesifik dari fitur Category diurutkan dari terbesar hingga terendah :
  - Taman Hiburan : 3053 sample, 30.5%
  - Budaya : 2683 sample, 26.8%
  - Cagar Alam : 2415 sample, 24.2%
  - Bahari : 1079 sample, 10.8%
  - Pusat Perbelanjaan : 385 sample, 3.8%
  - Tempat Ibadah : 385 sample, 3.8%
"""

print('Banyak tempat wisata : ', len(all_tourism['Place_Name'].unique()))
print('Nama Tempat : ', all_tourism['Place_Name'].unique())

"""Untuk fitur Place_Name disini hanya menampilkan banyak tempat wisata. Diperoleh bahwa banyak tempat wisata yang akan digunakan untuk sistem rekomendasi adalah sebanyak 437.

# **DATA PREPARATION**
"""

#cek null value
all_tourism.isnull().sum()

len(all_tourism.Place_Id.unique())

all_tourism['Category'].unique()

#mengurutkan Place_Id
preparation = all_tourism
preparation.sort_values('Place_Id')

"""Place_Id diurutkan untuk mengetahui apakah terdapat data duplikat atau tidak"""

preparation = preparation.drop_duplicates('Place_Id')
preparation

#membuat variabel baru untuk dictianory
place_id = preparation['Place_Id'].tolist()
place_category = preparation['Category'].tolist()
place_name = preparation['Place_Name'].tolist()

print(len(place_id))
print(len(place_category))
print(len(place_name))

#membuat dictianory tourism_recommend
tourism_recommend = pd.DataFrame({
    'id' : place_id,
    'place_category' : place_category,
    'place_name' : place_name
})

tourism_recommend

"""Dibuatnya tourism_recommend untuk menampung fitur-fitur yang hanya akan digunakan untuk rekomendasi

# **MODELLING | CONTENT BASED FILTERING**
"""

data = tourism_recommend
data.head()

tf = TfidfVectorizer()
tf.fit(data['place_name'])
tf.get_feature_names_out()

"""Membuat sistem rekomendasi berdasarkan tempat wisata yang telah dikunjungi sebelummnya, menggunakan TF-IDF Vectorizer dengan fungsi `tfidfvectorizer()` dari sklearn. Tahap ini terdiri dari inisialisasi TfidfVectorizer, kemudian perhitungan idf pada place_name dan mapping array dari fitur index ke fitur nama."""

#mengubah data dalam bentuk matrix integer
tfdif_matrix = tf.fit_transform(data['place_name'])
tfdif_matrix.shape

#mengubah vektor tf-dif dalam bentuk matrix
tfdif_matrix.todense()

pd.DataFrame(
    tfdif_matrix.todense(),
    columns = tf.get_feature_names_out(),
    index = data.place_category  
).sample(22, axis = 1).sample(10, axis = 0)

"""Membuat dataframe untuk melihat tf-idf matrix dengan kolom berisi place_name dan baris place_category, ini digunakan untuk melihat korelasi antar place_name dengan category.

**COSINE SIMILARITY**
"""

cosine_sim = cosine_similarity(tfdif_matrix)
cosine_sim

cosine_sim_df = pd.DataFrame(cosine_sim, index = data['place_name'], columns = data['place_name'])
print('Shape : ', cosine_sim_df.shape)

cosine_sim_df.sample(5, axis = 1).sample(10, axis = 0)

"""Menghitung derajat kesamaan (similarity degree) antar place_name menggunakan cosine_similarity dari sklearn"""

#fungsi untuk rekomendasi
def tourism_recommendations(nama_tempat, similarity_data = cosine_sim_df, items = data[['place_name', 'place_category']], k = 5) :
  index = similarity_data.loc[:, nama_tempat].to_numpy().argpartition(
      range(-1, -k, -1)
  )

  closest = similarity_data.columns[index[-1:-(k+2):-1]]
  closest = closest.drop(nama_tempat, errors = 'ignore')

  return pd.DataFrame(closest).merge(items).head(k)

data[data.place_name.eq('Pantai Baron')]

tourism_recommendations('Pantai Baron')

"""# **MODELLING | COLLABORATIVE FILTERING**"""

cf = preparation
cf

user_ids = cf['User_Id'].unique().tolist()
print('list User_Id : ', user_ids)

user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}
print('encoded User_Id : ', user_to_user_encoded)

user_encoded_to_user = {i: x for i, x in enumerate(user_ids)}
print('encoded angka ke User_Id : ', user_encoded_to_user)

place_ids = cf['Place_Id'].unique().tolist()
print('list Place_Id : ', place_ids)

place_to_place_encoded = {x: i for i, x in enumerate(place_ids)}
print('encoded Place_Id : ', place_to_place_encoded)

place_encoded_to_place = {i: x for i, x in enumerate(place_ids)}
print('encoded angka ke Place_Id : ', place_encoded_to_place)

cf['user'] = cf['User_Id'].map(user_to_user_encoded)
cf['place'] = cf['Place_Id'].map(place_to_place_encoded)

num_users = len(user_to_user_encoded)
print(num_users)

num_places = len(place_encoded_to_place)
print(num_places)

cf['Place_Ratings'] = cf['Place_Ratings'].values.astype(np.float32)

min_rating = min(cf['Place_Ratings'])

max_rating = max(cf['Place_Ratings'])

print('Number of User : {}, Number of Place : {}, Min Rating {}, Max Rating {}'.format(
    num_users, num_places, min_rating, max_rating
))

"""- Encoder User_Id dan Place_Id menjadi indeks integer.
- Encoder User_Id dan Place_Id menjadi indeks integer.
- Mapping User_Id dan Place_Id kedalam proses encoder sebelumnya.

# **SPLITTINGA TRAINING & VALIDATION DATA**
"""

cf = cf.sample(frac = 1, random_state = 30)
cf

x = cf[['User_Id', 'Place_Id']].values

y = cf['Place_Ratings'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

train_indices = int(0.8 * df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

print(x, y)

"""- Distribusi data dengan random_state agar data menjadi acak.
- Mapping data User_Id dan Place_Id menjadi skala 0 sampai 1
- Split data train dan validation menjadi 80:20
"""

class RecommenderNet(tf.keras.Model):
 
  def __init__(self, num_users, num_places, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_places = num_places
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding(
        num_users,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )

    self.user_bias = layers.Embedding(num_users, 1)
    self.places_embedding = layers.Embedding(
        num_places,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.places_bias = layers.Embedding(num_places, 1)
  
  def call(self, inputs) :
    user_vector = self.user_embedding(inputs[:, 0])
    user_bias = self.user_bias(inputs[:, 0])
    places_vector = self.places_embedding(inputs[:, 1])
    places_bias = self.places_bias(inputs[:, 1])

    dot_user_places = tf.tensordot(user_vector, places_vector, 2)

    x = dot_user_places + user_bias + places_bias

    return tf.nn.sigmoid(x)

"""- Pada proses ini menghitung skor kecocokan wisatawan atau turis dengan destinasi wisata dengan teknik embedding.
- Membuat class RecommenderNet dengan keras Model class.
- Menginisialisasikan fungsi embedding.
- Membuat layer embedding user dan layer embedding user dengan bias.
- Membuat layer embedding place dan layer embedding place dengan bias.
- Membuat fungsi call yang memanggil layer embedding 1,2,3, dan 4.
- Kemudian menggunakan activation sigmoid.
- Lakukan compile pada model yang telah dibuat dengan loss `BinaryCrossentropy()`, optimizer `Adam()` dengan `learning_rate = 0.001`, dan metrics `RootMeanSquaredError()`.
- Lakukan proses training dengan `batch_size = 8` dan `epochs = 100`.
"""

model = RecommenderNet(num_users, num_places, 50)

model.compile(
    loss = tf.keras.losses.BinaryCrossentropy(),
    optimizer = keras.optimizers.Adam(learning_rate = 0.001),
    metrics = [tf.keras.metrics.RootMeanSquaredError()]
)

hist = model.fit(x = x_train, y = y_train, batch_size = 8, epochs = 100, validation_data = (x_val, y_val))

"""# **METRICS VISUALIZATION**"""

plt.plot(hist.history['root_mean_squared_error'])
plt.plot(hist.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc = 'upper left')
plt.show()

"""Dapat disumpulkan pada proses training nilai error akhir untuk training berada pada angka 0.29 dan error pada test pada angka 0.31. Sehingga nilai tersebut sudah cukup bagus untuk sistem rekomendasi `collaborative filtering`.

# **PLACES RECOMMENDATION**
"""

places_cf = tourism_recommend
cf = pd.read_csv('/content/drive/MyDrive/dataset/archive (21)/tourism_rating.csv')

cf['Place_Ratings'] = cf['Place_Ratings'].values.astype(np.float32)

user_id = cf.User_Id.sample(1).iloc[0]
places_visited_by_user = cf[cf.User_Id == user_id]

places_not_visited = places_cf[~places_cf['id'].isin(places_visited_by_user.Place_Id.values)]['id']
places_not_visited = list(
    set(places_not_visited)
    .intersection(set(place_to_place_encoded.keys()))
)

places_not_visited = [[place_to_place_encoded.get(x)] for x in places_not_visited]
user_encoder = user_to_user_encoded.get(user_id)
user_places_array = np.hstack(
    ([[user_encoder]] * len(places_not_visited), places_not_visited)
)

"""Agar mendapatkan rekomendasi destinasi wisata, sebaiknya acak sample yang didefinisikan pada places_not_visited menggunakan operator bitwise (~) yang diperoleh pada variabel places_visited_by_user."""

ratings = model.predict(user_places_array).flatten()

top_ratings_indices = ratings.argsort()[-10:][::-1]
recommended_places_ids = [
    place_encoded_to_place.get(places_not_visited[x][0]) for x in top_ratings_indices
]

print('Showing recommendations for users : {}'.format(user_id))
print('===' * 9)
print('Place with high ratings from user')
print('----' * 8)

top_places_user = (
    places_visited_by_user.sort_values(
        by = 'Place_Ratings',
        ascending=False
    )
    .head(5)
    .Place_Id.values
)
 
places_df_rows = places_cf[places_cf['id'].isin(top_places_user)]
for row in places_df_rows.itertuples():
  print(row.place_name, ':', row.place_category)

print('----' * 8)
print('Top 10 place recommendation')
print('----' * 8)

recommended_places = places_cf[places_cf['id'].isin(recommended_places_ids)]
for row in recommended_places.itertuples():
  print(row.place_name, ':', row.place_category)