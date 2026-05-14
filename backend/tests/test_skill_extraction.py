from app.ai.skills.extractor import SkillExtractionEngine


def test_skill_extraction_expands_modern_backend_aliases() -> None:
    engine = SkillExtractionEngine()
    text = (
        'Experience with ASP.NET Core, EF Core, Entity Framework, Express.js, Node.js, REST API, Hibernate.'
    )
    result = engine.extract(text, section_lines=[text])

    assert result.skills == [
        'ASP.NET Core',
        'EF Core',
        'Entity Framework',
        'Express.js',
        'Node.js',
        'RESTful API',
        'Hibernate',
    ]
    assert result.categorized_skills['backend'] == [
        'ASP.NET Core',
        'EF Core',
        'Entity Framework',
        'Express.js',
        'Node.js',
        'RESTful API',
        'Hibernate',
    ]


def test_skill_extraction_identifies_databases_and_tools() -> None:
    engine = SkillExtractionEngine()
    text = 'Worked with SQL Server, PostgreSQL, Redis, SQLite, Docker, GitHub, Git, Postman, Jira, Railway, Render, Cloudinary.'
    result = engine.extract(text, section_lines=[text])

    assert result.skills == [
        'SQL Server',
        'PostgreSQL',
        'Redis',
        'SQLite',
        'Docker',
        'GitHub',
        'Git',
        'Postman',
        'Jira',
        'Railway',
        'Render',
        'Cloudinary',
    ]
    assert result.categorized_skills['database'] == ['SQL Server', 'PostgreSQL', 'Redis', 'SQLite']
    assert result.categorized_skills['devops'] == ['Docker']
    assert result.categorized_skills['tools'] == [
        'GitHub',
        'Git',
        'Postman',
        'Jira',
        'Railway',
        'Render',
        'Cloudinary',
    ]


def test_skill_extraction_normalizes_frontend_variants() -> None:
    engine = SkillExtractionEngine()
    text = 'Frontend work includes ReactJS, react.js, Next.js, TailwindCSS, Vue.js.'
    result = engine.extract(text, section_lines=[text])

    assert result.skills == ['React', 'Next.js', 'Tailwind CSS', 'Vue.js']
    assert result.categorized_skills['frontend'] == ['React', 'Next.js', 'Tailwind CSS', 'Vue.js']
