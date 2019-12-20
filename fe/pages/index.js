import React, { Fragment } from 'react'
import getSynonym from "./modules/getSyononym";
import getRelatedWord from "./modules/getRelatedWord";
import searchDocs from "./modules/searchDocs";
import countWords from "./modules/countWords";
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

export default function App() {
  const [searchTerm, setSearchTerm] = React.useState("明るい 人柄");
  const [terms, setTerms] = React.useState([]);
  const [searchResults, setSearchResults] = React.useState({});
  const [relatedWordResults, setRelatedWordResults] = React.useState({});
  const [baseDocResults, setBaseDocResults] = React.useState(null);
  const [wordCountResults, setWordCountResults] = React.useState({});
  const [loaded, setLoaded] = React.useState(false);
  const handleChange = event => {
    setSearchTerm(event.target.value);
  };
  const handleSearch = async () => {
    setLoaded(false);
    setBaseDocResults(null);
    const terms = searchTerm.split(/\s/).filter(s => s.length > 0);
    setTerms([...terms])
    const [synonyms, relatedWord, baseDocs] = await Promise.all([
      Promise.all(terms.map(async term => [term, await getSynonym(term)])),
      terms.length > 1 ? getRelatedWord(terms): null,
      searchDocs(terms),
    ])
    setBaseDocResults(baseDocs);
      
    const syonoymResults = synonyms.reduce((acc, [term, syonoymList]) => ({
        ...acc,
        [term]: syonoymList,
    }), {});
    setSearchResults(syonoymResults);
    setRelatedWordResults(relatedWord);
    setLoaded(true);
    const wordList = [
      ...synonyms.reduce((acc, [_, syonoymList])=> [...acc, ...syonoymList.map(({word}) => word)], []),
      ...(Array.isArray(relatedWord) ? relatedWord.map(({word}) => word): []),
    ];
    const wordCounts = await countWords(wordList);
    setWordCountResults(wordCounts);
    terms.map(async (term, i) => {
      const pre = terms.slice(0, i);
      const post = terms.slice(i+1);
      const synonyms = syonoymResults[term];
      const alternatives = pickWordsWithOccurrence(synonyms, wordCounts);
      const searches = await searchAlternatives(pre, post, alternatives);
      console.log(searches);
    })
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
                  Array.isArray(searchResults[term]) && searchResults[term].map(
                    ({ word }) => (
                      <Syononym count={wordCountResults[word]} key={word}>
                        {word}
                        <WordCount count={wordCountResults[word]}>
                          {typeof wordCountResults[word] === "number" ? `(${wordCountResults[word]})`: "(*)"}
                        </WordCount>
                      </Syononym>
                    )
                )}
              </SyonoymList>
            </SyononymResult>
          ))}
          {loaded && terms.length > 1 && (
              <RelatedWordResult>
                <RelatedWordHeader>関連語:{terms.join(" × ")}</RelatedWordHeader>
              <SyonoymList>
                {
                  Array.isArray(relatedWordResults) && relatedWordResults.map(
                    ({ word }) => (
                        <Syononym count={wordCountResults[word]} key={word}>
                          {word}
                          <WordCount count={wordCountResults[word]}>
                            {typeof wordCountResults[word] === "number" ? `(${wordCountResults[word]})`: "(*)"}
                          </WordCount>
                        </Syononym>
                    )
                )}
              </SyonoymList>
            </RelatedWordResult>
          )}
          </WordResults>
          <SearchResults>
            <SearchResult searchResults={baseDocResults} />
          </SearchResults>
      </Wrap>
  );
}

function SearchResult({ searchResults }) {
  if(!searchResults) {
    return null;
  }
  const { terms, total, results }= searchResults;
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