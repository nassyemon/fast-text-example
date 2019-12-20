export const pickWordsWithOccurrence = (terms, wordCounts) => terms.map(
    ({ word }) => typeof wordCounts[word] === "number" &&  wordCounts[word] > 0 ? word: null
  ).filter(v => v !== null);