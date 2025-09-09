# Algorithm comparison — Milestone 2 (28 Aug)

## Summary
Short summary of objective and dataset characteristics (tabular, mix of continuous/categorical, moderate size, label imbalance possible).

---

## Logistic Regression
**Description:** Linear model for binary classification.  
**Pros:** Interpretable coefficients, fast, robust with regularization, works well as baseline.  
**Cons:** Linear decision boundary; needs feature scaling; can underfit complex relationships.  
**Use for Framingham:** Good baseline. Use `class_weight='balanced'` if classes imbalanced.  
**Tuning:** regularization C, penalty (l1/l2), solver.

---

## Random Forest
**Description:** Ensemble of decision trees.  
**Pros:** Handles non-linear relations, robust to outliers, gives feature importance.  
**Cons:** Less interpretable, can overfit if not tuned, heavier compute.  
**Use:** Strong candidate for baseline + feature importance.  
**Tuning:** n_estimators, max_depth, min_samples_leaf, max_features.

---

## SVM (linear & RBF)
**Description:** Max-margin classifier; supports kernels.  
**Pros:** Effective in high-dimensional spaces; robust with proper scaling.  
**Cons:** Sensitive to scale; expensive on large datasets; probabilistic outputs require calibration.  
**Tuning:** C, kernel (linear/RBF), gamma (for RBF), probability=True.

---

## Neural Network (MLP)
**Description:** Feed-forward MLP handling non-linearities.  
**Pros:** Can model complex relations, flexible architecture.  
**Cons:** Needs tuning, regularization, and more data; less interpretable.  
**Tuning:** number of layers, units, learning rate, batch_size, dropout.

---

## Comparison Matrix
| Algorithm           | Interpretability | Training time | Handles Nonlinear | Robust to Outliers | Good for Small-Medium Data |
|-------------------- |------------------|---------------|-------------------|--------------------|----------------------------|
| Logistic Regression | High             | Very low      | No                | Moderate           | Yes                        |
| Random Forest       | Medium           | Moderate      | Yes               | Yes                | Yes                        |
| SVM (RBF)           | Low              | High          | Yes               | Moderate           | Maybe                      |
| Neural Net          | Low              | High          | Yes               | Sensitive          | No (unless enough data)    |

