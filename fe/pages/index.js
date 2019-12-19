import React from 'react'
import styled from 'styled-components';
import getSynonym from "./modules/getSyononym";
import getRelatedWord from "./modules/getRelatedWord";

export default function App() {
  const [searchTerm, setSearchTerm] = React.useState("明るい 人柄");
  const [terms, setTerms] = React.useState([]);
  const [searchResults, setSearchResults] = React.useState({});
  const [relatedWordResults, setRelatedWordResults] = React.useState({});
  const [loaded, setLoaded] = React.useState(false);
  const handleChange = event => {
    setSearchTerm(event.target.value);
  };
  const handleClick = async () => {
    setLoaded(false);
    const terms = searchTerm.split(/\s/).filter(s => s.length > 0);
    setTerms(terms)
    const [synonyms, relatedWord] = await Promise.all([
      Promise.all(terms.map(async term => [term, await getSynonym(term)])),
      terms.length > 1 ? getRelatedWord(terms): null,
    ])
      
    const syonoymResults = synonyms.reduce((acc, [term, result]) => ({
        ...acc,
        [term]: result,
    }), {});
    setSearchResults(syonoymResults);
    setRelatedWordResults(relatedWord);
    setLoaded(true);
  }
  const handleKeyDown = event => {
    if(event.keyCode == 13){
        handleClick();
    }
  }
/*
 React.useEffect(() => {
    const results = people.filter(person =>
      person.toLowerCase().includes(searchTerm)
    );
    setSearchResults(results);
  }, [searchTerm]);
*/
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
            <SearchButton onClick={handleClick}>検索</SearchButton>
        </Search>
        <WordResults>
          {terms.map(term => (
            <SyononymResult key={term}>
              <SyononymHeader>類語:{term}</SyononymHeader>
              <SyonoymList>
                {
                  Array.isArray(searchResults[term]) && searchResults[term].map(
                        ({ i, word }) => (
                          <Syononym key={word}>
                            {word}
                          </Syononym>
                    )
                )}
              </SyonoymList>
            </SyononymResult>
          ))}
          {loaded && terms.length > 1 && (
              <RelatedWordResult>
                <RelatedWordHeader>関連語:{terms.join(" × ")}</RelatedWordHeader>
                <RelatedWordList>
                  {
                    Array.isArray(relatedWordResults) && relatedWordResults.map(
                          ({ i, word }) => (
                            <RelatedWord key={word}>
                              {word}
                            </RelatedWord>
                      )
                  )}
              </RelatedWordList>
            </RelatedWordResult>
          )}
          </WordResults>
      </Wrap>
  );
}

 const Search = styled.div`
  width: 50%;
  position: relative;
  display: flex;
`;

const SearchTerm = styled.input.attrs({
    type: "text"
})`
  width: 100%;
  border: 3px solid #00B4CC;
  border-right: none;
  padding: 5px;
  height: 20px;
  border-radius: 5px 0 0 5px;
  outline: none;
  color: #555555;
  &:focus {
    font-weight: bold;
    color: #000000;
  },
`;

const SearchButton = styled.button.attrs({ 
    type: "submit"
})`
  width: 80px;
  height: 36px;
  border: 1px solid #00B4CC;
  background: #00B4CC;
  text-align: center;
  color: #fff;
  border-radius: 0 5px 5px 0;
  cursor: pointer;
  font-size: 20px;
`;

const Wrap = styled.div`
  width: 100%;
  top: 10%;
  left: 10%;
  position: absolute;
`;

const WordResults = styled.div`
  width: 80%;
  position: relative;
`;

const SyononymResult = styled.div`
  width: 100%;
  margin: 20px 0px;
  position: relative;
  display: flex;
  flex-direction: column;
  border: 3px solid #00B4CC;
`

const SyononymHeader = styled.h3`
  padding-left: 10px;
  margin: 0px;
  font-weight: bolder;
  background: #00B4CC;
  color: #ffffff;
`;

const SyonoymList = styled.div`
  display:flex;
  flex-direction: row;
  flex-wrap: wrap;
`

const Syononym = styled.span`
  margin: 0px 5px;
`;

const RelatedWordResult = styled(SyononymResult)`
  border-color: #cc317c;
`

const RelatedWordHeader = styled(SyononymHeader)`
  background: #cc317c;
`;

const RelatedWordList = styled(SyonoymList)`
`

const RelatedWord = styled(Syononym)`
`;