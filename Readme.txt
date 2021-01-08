The project is a recommendation engine which, at this moment is capable to predict movies which user could like based upom his/her past experience. Predicting rating just based upon the user's past likes and dislikes may seem redundant as it doesn'nt include any other users. But, upto this moment this engine only recommends the best movies to the user which are demographic recommendations, if user has'nt given any rating yet and content based recommendations upon receiving user's input. While, i am still working on collabarative recommendations to create a hybrid system.

Features:
1. The database is checked by the program itself whether it is present in the relative path or not. Whether each file is present or not. If not, data is automatically downloaded using IBM object storage api having my personal object storage credentials.
2. It calculates demographic recommendations for default user(best rated movies according to IMDB rating system).
3. The program is loaded with a search engine for searching movie names by user through the dataset using edit distance(levenshtien distance). The search engine also has reset feature to reset the input frame as any moment.
4. The content-based recommendations takes into consideration keywords and genres to predict movies.

Although the system works fine. But there are still a few things left.

The main script is "main_engine_101" while supportive functions are in "recom_al" and "recom_func".
