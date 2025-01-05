export interface IMatchedSource {
  type: string;
  source: string;
  similarity: number;
  sourceAnswer?: string;
  possiblePrompt?: string;
}
