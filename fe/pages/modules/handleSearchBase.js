import getSynonym from "./getSyononym";
import getRelatedWord from "./getRelatedWord";
import searchDocs from "./searchDocs";
import countWords from "./countWords";

export default async (searchTerm) => {
    console.error(searchTerm);
    const terms = searchTerm.split(/\s/).filter(s => s.length > 0);
    const [synonymResults, relatedWord, baseDocs] = await Promise.all([
      Promise.all(terms.map(async term => [term, await getSynonym(term)])),
      terms.length > 1 ? getRelatedWord(terms): null,
      searchDocs(terms),
    ])
    const synonyms = synonymResults.reduce((acc, [term, syonoymList]) => ({
        ...acc,
        [term]: syonoymList,
    }), {});
    const wordList = [
      ...synonymResults.reduce((acc, [_, syonoymList])=> [...acc, ...syonoymList.map(({word}) => word)], []),
      ...(Array.isArray(relatedWord) ? relatedWord.map(({word}) => word): []),
    ];
    const wordCounts = await countWords(wordList);
    return {
      terms,
      baseDocs,
      synonyms,
      relatedWord,
      wordCounts,
    };
};
