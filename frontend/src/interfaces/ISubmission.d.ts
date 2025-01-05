import { IMatchedSource } from "./IMatchedSource";
import { ISimiliarityResults } from "./ISimilarityResults";

export interface ISubmission {
  traineeNumber: string;
  forumQuestion: string;
  forumAnswer: string;
  similarityResults: ISimiliarityResults;
  overallPlagiarismScore: number;
  matchedSources: IMatchedSource[];
}