# **Kuvaus**
Sovellus, jonka avulla käyttäjä voi
seurata joukkoliikenteen
pysäkkien aikatauluja.

**Sovelluksen suunnitellut ominaisuudet**
- Kotinäkymä, josta käyttäjä näkee valitsemansa joukkoliikenteen pysäkit.
- Käyttäjä voi lisätä ja poistaa pysäkkejä kotinäkymästä.
- Valitsemalla pysäkin käyttäjälle avautuu tarkempi näkymä, josta näkyy saapuvien 
  bussien tai raitiovaunujen aikataulut. Käyttäjälle voidaan näyttää myös tietoa 
  häiriöstä tai viivästyksistä.
- Hakutoiminto, jonka avulla käyttäjä voi etsiä haluamansa pysäkit. Tarkempi     toteutus
  vielä epävarma, haku voisi toimia esimerkiksi pysäkin
  nimen tai koodin perusteella. Myös sijainnin tai linjan perusteella toimiva
  haku voisi olla mahdollinen.
- Käyttäjä voi antaa pysäkeille haluamansa lempinimen.
- Käyttäjä voi kirjautua sisään ja ulos sekä
  luoda uuden tunnuksen.

## **Käynnistämisohjeet**

Sovellus ei ole testattavissa Fly.io:ssa. Alla ohjeet paikalliseen
testaamiseen.

**HUOM:** Toimiakseen sovellus tarvitsee verkkoyhteyden.

**1. Kloonaa repositorio**
```
$ git clone https://github.com/user7888/pysakit-app.git
```
**2. Aktivoi virtuaaliympäristö ja asenna riippuvuudet**
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

**3. Määritä tietokannan skeema**
```
$ psql < schema.sql
```
**4. Määritä ympäristömuuttujat**

Luo tiedosto **.env** ja lisää sinne muuttujat:
```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```

**5. Käynnistä sovellus**
```
$ flask run
```

## **Projektin tilanne**

Toteutetut ominaisuudet
- Päänäkymä, jossa näytetään käyttäjän valitsemat pysäkit.
- Uuden pysäkin lisääminen.
- Hakutoiminto pysäkkien etsimiseen
- Pysäkin poistaminen.
- Yksittäisen pysäkin näkymä, jossa näkyy saapuvat joukkoliikennevälineet.
- Kirjautuminen ja käyttäjätunnuksen rekisteröinti.

Keskeneräiset
- Käyttäjä voi nimetä pysäkkejä.
- Virheidenkäsittelyn parantaminen.
- Visuaalisen ilmeen parantaminen.
- Enemmän infoa saapuvista joukkoliikennevälineistä
  yksittäisen pysäkin näkymään.
- Käytettävyyden ja ulkonäön parantelu.
- Oikeudet, syötteet ja tietoturva.




