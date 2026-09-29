import json
from pathlib import Path


JOBS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "jobs.json"
)


def normalize(value) -> str:
    if not value:
        return ""

    value = str(value).lower().strip()

    replacements = {
        "microsoft excel": "excel",
        "ms excel": "excel",
        "microsoft word": "word",
        "ms word": "word",
        "microsoft powerpoint": "powerpoint",
        "ms powerpoint": "powerpoint",
        "reactjs": "react.js",
        "react js": "react.js",
        "nextjs": "next.js",
        "next js": "next.js",
        "html5": "html",
        "css3": "css",
        "javascript (es6+)": "javascript",
        "javascript es6+": "javascript",
        "js": "javascript",
        "nodejs": "node.js",
        "node js": "node.js",
        "file and document management": "file management",
        "file & document management": "file management"
    }

    return replacements.get(value, value)


def load_jobs() -> list:
    with open(JOBS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def skill_matches(candidate_skill: str, job_skill: str) -> bool:
    candidate = normalize(candidate_skill)
    job = normalize(job_skill)

    if not candidate or not job:
        return False

    return (
        candidate == job
        or candidate in job
        or job in candidate
    )


def calculate_skill_score(
    candidate_skills: list,
    job_skills: list
) -> tuple:

    if not job_skills:
        return 100, [], []

    matched_skills = []

    for job_skill in job_skills:
        for candidate_skill in candidate_skills:
            if skill_matches(candidate_skill, job_skill):
                matched_skills.append(job_skill)
                break

    matched_skills = list(dict.fromkeys(matched_skills))

    matched_normalized = {
        normalize(skill)
        for skill in matched_skills
    }

    missing_skills = [
        skill
        for skill in job_skills
        if normalize(skill) not in matched_normalized
    ]

    score = (
        len(matched_skills) / len(job_skills)
    ) * 100

    return (
        round(score),
        matched_skills,
        missing_skills
    )


def calculate_experience_score(
    candidate_experience,
    required_experience
) -> int:

    try:
        candidate_experience = float(
            candidate_experience or 0
        )

        required_experience = float(
            required_experience or 0
        )

    except (ValueError, TypeError):
        return 0

    if required_experience <= 0:
        return 100

    if candidate_experience >= required_experience:
        return 100

    score = (
        candidate_experience / required_experience
    ) * 100

    return round(score)


def calculate_role_score(
    recommended_roles: list,
    job_title: str,
    job_roles: list
) -> int:

    candidate_roles = [
        normalize(role)
        for role in recommended_roles
    ]

    possible_job_roles = [
        normalize(role)
        for role in job_roles
    ]

    if job_title:
        possible_job_roles.append(
            normalize(job_title)
        )

    for candidate_role in candidate_roles:
        for job_role in possible_job_roles:

            if not candidate_role or not job_role:
                continue

            if (
                candidate_role == job_role
                or candidate_role in job_role
                or job_role in candidate_role
            ):
                return 100

    return 0


def build_match_reason(
    matched_skills: list,
    missing_skills: list,
    experience_score: int,
    role_score: int
) -> str:

    reasons = []

    if matched_skills:
        reasons.append(
            "Matched skills: "
            + ", ".join(matched_skills)
        )

    if experience_score == 100:
        reasons.append(
            "Experience meets the job requirement."
        )
    elif experience_score > 0:
        reasons.append(
            "Candidate has some relevant experience."
        )

    if role_score == 100:
        reasons.append(
            "Recommended role aligns with this position."
        )

    if missing_skills:
        reasons.append(
            "Missing skills: "
            + ", ".join(missing_skills)
        )

    if not reasons:
        return "Limited match with the current profile."

    return " ".join(reasons)


def match_jobs(
    candidate_profile: dict,
    top_n: int = 5
) -> list:

    jobs = load_jobs()

    candidate_skills = candidate_profile.get(
        "skills",
        []
    )

    candidate_experience = candidate_profile.get(
        "years_of_experience",
        0
    )

    recommended_roles = candidate_profile.get(
        "recommended_roles",
        []
    )

    matches = []

    for job in jobs:

        (
            skill_score,
            matched_skills,
            missing_skills
        ) = calculate_skill_score(
            candidate_skills,
            job.get("skills", [])
        )

        experience_score = calculate_experience_score(
            candidate_experience,
            job.get("experience_required", 0)
        )

        role_score = calculate_role_score(
            recommended_roles,
            job.get("title", ""),
            job.get("roles", [])
        )

        # Ignore unrelated jobs
        if role_score == 0 and skill_score < 60:
            continue

        final_score = (
            skill_score * 0.60
            + experience_score * 0.25
            + role_score * 0.15
        )

        # Ignore weak recommendations
        if final_score < 50:
            continue

        matches.append({
            "id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "type": job.get("type"),
            "match_score": round(final_score),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_required": job.get(
                "experience_required",
                0
            ),
            "reason": build_match_reason(
                matched_skills,
                missing_skills,
                experience_score,
                role_score
            )
        })

    matches.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return matches[:top_n]