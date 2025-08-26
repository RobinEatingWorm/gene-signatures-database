# Install required packages if needed
if (!requireNamespace("rjson", quietly = TRUE)) {
    install.packages("rjson")
}

# Read table of metrics
metrics <- read.csv(rjson::fromJSON(file = "paths.json")$analysis$metrics)
metrics <- metrics[order(metrics$set, metrics$prompt_number), ]

# Get validation metrics
val_metrics <- metrics[which(metrics$set == "val"), ]

# Plot validation accuracy
val_accuracy <- t(as.matrix(val_metrics[c("positive_accuracy", "negative_accuracy")]))
plot(NULL, type = "n", xlim = c(0, prod(dim(val_accuracy)) + ncol(val_accuracy) + 1), ylim = c(0, 1), ann = FALSE,
     axes = FALSE, xaxs = "i", yaxs = "i")
grid(nx = NA, ny = NULL)
barplot(val_accuracy, names.arg = val_metrics$prompt_number, beside = TRUE, col = c(3, 2), border = NA, add = TRUE)
legend("topright", c("Positve Accuracy", "Negative Accuracy"), fill = c(3, 2), border = NA)
title(main = "Prompt Validation Accuracies", xlab = "Prompt Number", ylab = "Accuracy")
box(bty = "o")

# Plot validation cost
val_cost <- t(as.matrix(val_metrics[c("cost_input", "cost_output")]))
plot(NULL, type = "n", xlim = c(0, prod(dim(val_cost)) + ncol(val_cost) + 1), ylim = c(0, 0.02), ann = FALSE,
     axes = FALSE, xaxs = "i", yaxs = "i")
grid(nx = NA, ny = NULL)
barplot(val_cost, names.arg = val_metrics$prompt_number, beside = TRUE, col = c(4, 7), border = NA, add = TRUE)
legend("topright", c("Input Cost", "Output Cost"), fill = c(4, 7), border = NA)
title(main = "Prompt Costs on Validation Set", xlab = "Prompt Number", ylab = "Cost (dollars)")
box(bty = "o")
