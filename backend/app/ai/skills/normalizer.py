from __future__ import annotations

import re

NORMALIZATION_MAP: dict[str, str] = {
    'reactjs': 'React',
    'react.js': 'React',
    'react': 'React',
    'vuejs': 'Vue.js',
    'vue.js': 'Vue.js',
    'vue': 'Vue.js',
    'angularjs': 'Angular',
    'angular': 'Angular',
    'nextjs': 'Next.js',
    'next.js': 'Next.js',
    'tailwindcss': 'Tailwind CSS',
    'tailwind css': 'Tailwind CSS',
    'tailwind': 'Tailwind CSS',
    'fastapi': 'FastAPI',
    'mongodb': 'MongoDB',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'mysql': 'MySQL',
    'sql server': 'SQL Server',
    'redis': 'Redis',
    'sqlite': 'SQLite',
    'nodejs': 'Node.js',
    'node.js': 'Node.js',
    'node': 'Node.js',
    'expressjs': 'Express.js',
    'express.js': 'Express.js',
    'express': 'Express.js',
    'github actions': 'GitHub Actions',
    'github': 'GitHub',
    'git': 'Git',
    'gitlab': 'GitLab',
    'gcp': 'Google Cloud',
    'google cloud platform': 'Google Cloud',
    'aws': 'AWS',
    'azure': 'Azure',
    'docker': 'Docker',
    'k8s': 'Kubernetes',
    'kubernetes': 'Kubernetes',
    'rails': 'Ruby on Rails',
    'ruby on rails': 'Ruby on Rails',
    'spring boot': 'Spring Boot',
    'springboot': 'Spring Boot',
    'hibernate': 'Hibernate',
    'asp.net': 'ASP.NET',
    'aspnet': 'ASP.NET',
    'asp.net core': 'ASP.NET Core',
    'aspnet core': 'ASP.NET Core',
    'aspnetcore': 'ASP.NET Core',
    'entity framework': 'Entity Framework',
    'ef core': 'EF Core',
    'efcore': 'EF Core',
    'entity framework core': 'EF Core',
    'entityframeworkcore': 'EF Core',
    'rest api': 'RESTful API',
    'restful api': 'RESTful API',
    'postman': 'Postman',
    'jira': 'Jira',
    'railway': 'Railway',
    'render': 'Render',
    'cloudinary': 'Cloudinary',
    'pytest': 'pytest',
    'unittest': 'unittest',
    'jest': 'Jest',
    'mocha': 'Mocha',
    'cypress': 'Cypress',
    'selenium': 'Selenium',
    'playwright': 'Playwright',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'scikit-learn': 'scikit-learn',
    'scikitlearn': 'scikit-learn',
    'hugging face': 'Hugging Face',
    'spacy': 'spaCy',
    'spaCy': 'spaCy',
    'pandas': 'pandas',
    'numpy': 'NumPy',
    'opencv': 'OpenCV',
    'php': 'PHP',
    'typescript': 'TypeScript',
    'javascript': 'JavaScript',
    'html': 'HTML',
    'css': 'CSS',
    'swiftui': 'SwiftUI',
    'react native': 'React Native',
    'flutter': 'Flutter',
    'kotlin multiplatform': 'Kotlin Multiplatform',
}


def normalize_skill(raw_skill: str) -> str:
    # Normalize skill variants into canonical taxonomy names.
    # This function supports alternate spellings, punctuation variants, and case.
    cleaned = raw_skill.strip()
    key = cleaned.lower()
    if key in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[key]

    simplified = re.sub(r'[\s\.\-_]+', ' ', key).strip()
    if simplified in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[simplified]

    compact = re.sub(r'[^a-z0-9#+]+', '', key)
    if compact in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[compact]

    return cleaned


def normalize_skills(raw_skills: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for skill in raw_skills:
        value = normalize_skill(skill)
        normalized_value = value.lower().strip()
        if normalized_value and normalized_value not in seen:
            seen.add(normalized_value)
            normalized.append(value)
    return normalized
