import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file1")
parser.add_argument("file2")
args = parser.parse_args()

# Load tables
df1 = pd.read_csv(args.file1)
df2 = pd.read_csv(args.file2)

# Align (assumes same ordering)
models = ["Parabolic", "Kane", "Taylor"]

diffs = {}

for m in models:
    diffs[m] = (df1[m] - df2[m]).abs()

# Build result table
out = pd.DataFrame({
    "Level": df1["Level"],
    "Parabolic_diff": diffs["Parabolic"],
    "Kane_diff": diffs["Kane"],
    "Taylor_diff": diffs["Taylor"],
})

# Totals
# Mean absolute differences
means = out[["Parabolic_diff", "Kane_diff", "Taylor_diff"]].mean()

# Overall mean across all values
overall_mean = means.mean()

print(out)
print("\nMean absolute differences (meV):")
print(means)

print("\nOverall mean absolute difference (meV):")
print(overall_mean)