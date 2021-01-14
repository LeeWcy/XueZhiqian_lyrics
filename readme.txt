脚本说明：
./data_crawl/data_crawling.py 从网易云音乐中爬取薛之谦的歌曲
./data_crawl/data_processing.py 处理爬取到的数据，去除非歌词信息
./lstm_model/train_lstm_word_based.py 训练lstm模型
./lstm_model/generate_lyrics_word_based.py 用训练好的lstm模型生成指定长度歌词
./seq2seq_model/train_seq2seq_word_based.py 训练seq2seq模型
./seq2seq_model/generation_word_based.py 用训练好的seq2seq模型生成指定长度歌词

./checkpoint 保存训练好的模型
./tensorboard_log_* tesnorboard文件

