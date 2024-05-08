# Given data
data = {
    "User A": [2.5, 2.5, 3.5, 3.0, 4.5],
    "User B": [3.0, 3.5, 2.0, 4.0, 1.5]
}


# Calculate cosine similarity
def cosine_similarity(user1, user2):
    dot_product = sum(a * b for a, b in zip(user1, user2))
    magnitude_user1 = sum(a ** 2 for a in user1) ** 0.5
    magnitude_user2 = sum(a ** 2 for a in user2) ** 0.5
    return dot_product / (magnitude_user1 * magnitude_user2)


# Extract user data
user_a_ratings = data["User A"]
user_b_ratings = data["User B"]

# Calculate and display cosine similarity
similarity = cosine_similarity(user_a_ratings, user_b_ratings)
print(similarity)
