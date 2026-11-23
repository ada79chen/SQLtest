# 數織 (Nonogram) 解題流程

當使用者傳來數織遊戲截圖時：

1. 從截圖讀出提示數字：左側為橫列（由上到下，每列從左到右讀），上方為直行（由左到右，每行從上到下讀）。
2. 寫入 `nonogram/puzzles/levelNN.txt`（NN 用截圖上的「第NN關」，格式參考 `level42.txt`）。
3. 執行 `python3 nonogram/solver.py nonogram/puzzles/levelNN.txt -o nonogram/puzzles/levelNN.png`。
4. 若程式回報「總格數不符」或「無解」，代表數字讀錯：重新對照截圖修正後再跑。
5. 用 SendUserFile 傳答案圖片給使用者，並以繁體中文簡短說明。
