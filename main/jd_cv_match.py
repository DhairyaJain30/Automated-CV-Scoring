from gensim.models.doc2vec import Doc2Vec
import numpy as np
from numpy.linalg import norm

def compute_similarity(jd_text, resume_text, model_path="C:\Coding\AI Resume Scorer\Models\content\cv_job_maching.model"):
    # Loading trained Doc2Vec model
    model = Doc2Vec.load(model_path)

    # Infer vectors
    v1 = model.infer_vector(resume_text.split())
    v2 = model.infer_vector(jd_text.split())

    # similarity formula
    similarity = 100 * (np.dot(v1, v2)) / (norm(v1) * norm(v2))
    return round(similarity, 2)
