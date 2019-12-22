import React, { Fragment } from 'react'
import Router, { useRouter } from "next/router";
import Link from 'next/link'
import getSynonym from "./modules/getSyononym";
import getRelatedWord from "./modules/getRelatedWord";
import searchDocs from "./modules/searchDocs";
import countWords from "./modules/countWords";
import handleSearchBase from "./modules/handleSearchBase";
import searchAlternatives from "./modules/searchAlternatives";
import { pickWordsWithOccurrence } from "./modules/utils";
import {
  Search,
  SearchTerm,
  SearchButton,
  Wrap,
  WordResults,
  SyononymResult,
  SyononymHeader,
  SyonoymList,
  Syononym,
  RelatedWordResult,
  RelatedWordHeader,
  WordCount,
} from "./atoms/styled";
import {
  SearchResults,
  BaseSearchResult,
  BaseSearchHeader,
  BaseSearchList,
  BaseSearchItem,
  SearchItemSpan,
  SearchItemHighlight,
} from "./atoms/searchWords";

const DEFAULT_SEARCH_TERMS = "明るい 人柄";

/*
terms,
baseDocs,
syonoymResults,
relatedWord,
wordCounts,
*/
function App(props) {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = React.useState(props.searchTerm || DEFAULT_SEARCH_TERMS);
  const [terms, setTerms] = React.useState(props.terms || []);
  const [relatedWord, setRelatedWord] = React.useState(props.relatedWord || {});
  const [baseDocs, setBaseDocs] = React.useState(props.baseDocs || null);
  const [wordCounts, setWordCounts] = React.useState(props.wordCounts || {});
  const [synonyms, setSynonyms] = React.useState(props.synonyms || {});
  const [loaded, setLoaded] = React.useState(props.loaded || false);
  const handleChange = event => {
    setSearchTerm(event.target.value);
  };
  const handleSearch = async () => {
    router.push(Router.pathname, `/?q=${searchTerm}`, { shallow: true });
    const ret = await handleSearchBase(searchTerm)
    setLoaded(false);
    setBaseDocs(null);
    setTerms([...ret.terms]);
    setBaseDocs(baseDocs);
    setSynonyms(ret.synonyms);
    setRelatedWord(ret.relatedWord);
    setWordCounts(ret.wordCounts);
    const { terms, synonyms } = ret;
    terms.map(async (term, i) => {
      const pre = terms.slice(0, i);
      const post = terms.slice(i+1);
      const synonymForTerm = synonyms[term];
      const alternatives = pickWordsWithOccurrence(synonymForTerm, wordCounts);
      const searches = await searchAlternatives(pre, post, alternatives);
      console.log(searches);
    })
    setLoaded(true);
  }
  const handleKeyDown = event => {
    if(event.keyCode == 13){
      handleSearch();
    }
  }
  return (
      <Wrap>
        <Search>
            <SearchTerm
                type="text"
                placeholder="検索語1 検索語2"
                value={searchTerm}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
            />
            <SearchButton onClick={handleSearch}>検索</SearchButton>
        </Search>
        <WordResults>
          {terms.map(term => (
            <SyononymResult key={term}>
              <SyononymHeader>類語:{term}</SyononymHeader>
              <SyonoymList>
                {
                  Array.isArray(synonyms[term]) && synonyms[term].map(
                    ({ word }) => (
                      <Syononym count={wordCounts[word]} key={word}>
                        {word}
                        <WordCount count={wordCounts[word]}>
                          {typeof wordCounts[word] === "number" ? `(${wordCounts[word]})`: "(*)"}
                        </WordCount>
                      </Syononym>
                    )
                )}
              </SyonoymList>
            </SyononymResult>
          ))}
          {Array.isArray(relatedWord) && (
              <RelatedWordResult>
                <RelatedWordHeader>関連語:{terms.join(" × ")}</RelatedWordHeader>
              <SyonoymList>
                {
                  relatedWord.length > 0 && relatedWord.map(
                    ({ word }) => (
                        <Syononym count={wordCounts[word]} key={word}>
                          {word}
                          <WordCount count={wordCounts[word]}>
                            {typeof wordCounts[word] === "number" ? `(${wordCounts[word]})`: "(*)"}
                          </WordCount>
                        </Syononym>
                    )
                )}
              </SyonoymList>
            </RelatedWordResult>
          )}
          </WordResults>
          <SearchResults>
            <SearchResult synonymResults={baseDocs} />
          </SearchResults>
      </Wrap>
  );
}

App.getInitialProps = async ({ query }) => {
  console.error(query);
  const searchTerm = query.q || DEFAULT_SEARCH_TERMS;
  const {
    terms,
    baseDocs,
    synonyms,
    relatedWord,
    wordCounts,
  } = await handleSearchBase(searchTerm);
  return {
    searchTerm,
    terms,
    baseDocs,
    synonyms,
    relatedWord,
    wordCounts,
    loaded: false,
  };
}

export default App;

function SearchResult({ synonymResults }) {
  if(!synonymResults) {
    return null;
  }
  const { terms, total, results }= synonymResults;
  if (!Array.isArray(terms)) {
    return <div>"term error"</div>;
  }
  const title = Array.isArray(results) && total > 0 ?
     `検索結果：${terms.join(" × ")} - 全${total}件中${results.length}件を表示`
     : `検索結果：${terms.join(" × ")} 0件`
  return (
    <BaseSearchResult>
      <BaseSearchHeader>{title}</BaseSearchHeader>
      {results.map(item => (
        <BaseSearchItem key={item.doc_id}>
          {SearchItemText(item)}
        </BaseSearchItem>
      ))}
    </BaseSearchResult>
  );
}

function SearchItemText({ text, highlight }) {
  if (!Array.isArray(highlight)) {
    return <SearchItemSpan >{text}</SearchItemSpan>;
  }
  return highlight.map(([fragment, hilighted], i) => hilighted? (
    <SearchItemHighlight key={i}>{fragment}</SearchItemHighlight>
  ) : (<SearchItemSpan key={i}>{fragment}</SearchItemSpan>)
  );
}