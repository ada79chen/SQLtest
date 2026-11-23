# 數織解題程式

```
python3 solver.py puzzles/level42.txt -o puzzles/level42.png
```

題目檔格式見 `puzzles/level42.txt`：`rows:` 下每行一列提示，`cols:` 下每行一行提示，數字用空白分隔，空行寫 0。
程式會先檢查橫列與直行總格數是否一致，再用逐線推理＋回溯求解，並檢查是否唯一解。需要 Pillow 才能輸出圖片。
