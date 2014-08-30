# Seger

A Chinese Keyword Extraction based on SAE Segmentation Service

## Descriptions

This application should be deployed to SAE.

* SAE's [Chinese segmentation service](http://sae.sina.com.cn/doc/python/segment.html) is used
* Based on TF-IDF method
* Corpus data is provided by [语料库在线](http://www.cncorpus.org/)

## Demo

* [Live Demo](http://catx.me/seger-demo/)

## API

> GET SERVICE_URL

### Parameters

Name     | Type   | Description
-------- | -----  | ------
c        | string | Chinese text
short    | bool   | Return keywords in short format (optional, default to `false`)
max      | int    | Max keywords count (optional, default to `10`)
callback | string | JSONP callback (optional, returns JSON format if not set)

### Response

#### Normal

```js
{
  "keywords": [/*...*/]
  "words": [/*...*/]
}
```

##### `keywords` Element Format

Short form: `string`

Long form:

Field    | Type   | Description
-------- | -----  | ----------
word     | string | The word
index    | string | Word index
word_tag | string | Word [tag](http://sae.sina.com.cn/doc/python/segment.html#api)
x        | float  | Weighted TF-IDF

##### `words` Element Format

Field    | Type   | Description
-------- | -----  | ----------
word     | string | The word
index    | string | Word index
word_tag | string | Word [tag](http://sae.sina.com.cn/doc/python/segment.html#api)
x        | float  | Weighted TF-IDF
lf       | float  | Local frequency (in current text)
gf       | float  | Global frequency (in corpus database)
tf_idf   | float  | TF-IDF

#### Error

```js
{
  "error": "error message"
}
```
