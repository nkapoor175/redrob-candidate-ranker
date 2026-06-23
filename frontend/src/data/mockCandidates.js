export const candidates = [
  {
    id: "1",
    rank: 1,
    name: "Rahul Sharma",
    role: "Senior Machine Learning Engineer",
    experienceYears: 6,
    finalScore: 92,
    scores: {
      skillMatch: 95,
      experience: 90,
      growth: 88,
      behavioral: 85
    },
    status: "Matched",
    skills: ["Python", "Machine Learning", "NLP", "FastAPI", "TensorFlow", "PyTorch"],
    projects: [
      {
        title: "NeuralRank API",
        description: "A high-throughput candidate scoring API using Transformer-based sentence embeddings and semantic matching, scaling to 10k requests/min."
      },
      {
        title: "AutoLabeler",
        description: "Unsupervised taxonomy alignment tool for resume-to-job description matching, reducing manual engineering labeling time by 70%."
      }
    ],
    reasoning: "Strong semantic alignment with required skills, relevant AI experience, and consistent career growth. Excellent fit for the Lead ML Architect role."
  },
  {
    id: "2",
    rank: 2,
    name: "Priya Patel",
    role: "AI Research Engineer",
    experienceYears: 4,
    finalScore: 89,
    scores: {
      skillMatch: 90,
      experience: 87,
      growth: 84,
      behavioral: 82
    },
    status: "Interviewing",
    skills: ["Python", "PyTorch", "Computer Vision", "OpenCV", "Docker", "FastAPI"],
    projects: [
      {
        title: "VisualQA Engine",
        description: "Visual question answering system using ViT (Vision Transformer) and GPT-2, deployed as a containerized microservice via Docker and FastAPI."
      },
      {
        title: "EdgeDetect SDK",
        description: "Optimized mobile-friendly image segmentation models, reducing model footprint by 60% while maintaining 95% mAP."
      }
    ],
    reasoning: "Deep understanding of deep learning models, solid research background in computer vision, and good software engineering standards."
  },
  {
    id: "3",
    rank: 3,
    name: "Amit Verma",
    role: "MLOps Engineer",
    experienceYears: 5,
    finalScore: 85,
    scores: {
      skillMatch: 88,
      experience: 82,
      growth: 86,
      behavioral: 84
    },
    status: "Matched",
    skills: ["Python", "Kubernetes", "MLflow", "AWS", "Docker", "Terraform"],
    projects: [
      {
        title: "AutoMLOps Pipeline",
        description: "Orchestrated end-to-end model training, registry, deployment, and shadow routing for 50+ production models using Kubeflow and GitOps."
      },
      {
        title: "ModelShield Monitor",
        description: "Real-time concept drift detection and API latency monitoring dashboard deployed across AWS EKS clusters."
      }
    ],
    reasoning: "Excellent system engineering skills, strong background in Kubernetes, MLflow, and CI/CD pipelines for large language models."
  },
  {
    id: "4",
    rank: 4,
    name: "Sneha Reddy",
    role: "Data Scientist",
    experienceYears: 3,
    finalScore: 82,
    scores: {
      skillMatch: 84,
      experience: 80,
      growth: 85,
      behavioral: 79
    },
    status: "Under Review",
    skills: ["Python", "SQL", "Pandas", "Scikit-Learn", "Tableau", "Machine Learning"],
    projects: [
      {
        title: "ChurnPredict System",
        description: "Customer churn prediction models with automated weekly predictive scoring and Tableau dashboard reporting for executive leadership."
      },
      {
        title: "SegmentAI",
        description: "Dynamic customer clustering framework utilizing RFM analysis and custom unsupervised K-Means algorithms."
      }
    ],
    reasoning: "Strong statistical background, solid experience in customer churn modeling, but slightly less deep learning experience than top candidates."
  },
  {
    id: "5",
    rank: 5,
    name: "Vikram Malhotra",
    role: "Senior Data Engineer",
    experienceYears: 7,
    finalScore: 78,
    scores: {
      skillMatch: 76,
      experience: 82,
      growth: 74,
      behavioral: 80
    },
    status: "Under Review",
    skills: ["SQL", "Python", "Apache Spark", "Airflow", "Snowflake", "AWS"],
    projects: [
      {
        title: "DataLake Core",
        description: "Designed and built a petabyte-scale lakehouse migration pipeline using Apache Spark, delta tables, and Apache Airflow DAGs."
      },
      {
        title: "StreamingRank Tracker",
        description: "Real-time event ingestion engine using Kafka, processing 50M+ daily events with sub-second delivery latency."
      }
    ],
    reasoning: "Strong SQL and data warehousing capabilities. Excellent backend pipeline builder, though lacks heavy machine learning or neural network experience."
  },
  {
    id: "6",
    rank: 6,
    name: "Ananya Sen",
    role: "Frontend Engineer (AI Tools)",
    experienceYears: 2,
    finalScore: 75,
    scores: {
      skillMatch: 72,
      experience: 70,
      growth: 82,
      behavioral: 76
    },
    status: "Rejected",
    skills: ["JavaScript", "React", "Tailwind CSS", "Python", "Node.js", "Vite"],
    projects: [
      {
        title: "PromptStudio UI",
        description: "Collaborative playground for prompt engineering with live system prompt evaluation, token counts, and cost estimates."
      },
      {
        title: "RecruiterDash v1",
        description: "Built the prototype recruitment visualization panel using Vite, Tailwind CSS, and simple charts."
      }
    ],
    reasoning: "Strong UI developer, has experience building React applications that integrate with AI systems, but has limited core AI training experience."
  }
];

export const statistics = {
  totalCandidates: 42,
  skillsExtracted: 156,
  averageMatchScore: 78,
  topRankedCandidate: "Rahul Sharma"
};

export const analyticsData = {
  scoreDistribution: [
    { range: "50-60", count: 3 },
    { range: "60-70", count: 8 },
    { range: "70-80", count: 15 },
    { range: "80-90", count: 12 },
    { range: "90-100", count: 4 }
  ],
  topSkills: [
    { name: "Python", value: 38 },
    { name: "Machine Learning", value: 28 },
    { name: "Docker", value: 24 },
    { name: "PyTorch", value: 20 },
    { name: "SQL", value: 18 },
    { name: "FastAPI", value: 15 }
  ],
  radarComparison: [
    { subject: "Skill Match", "Rahul Sharma": 95, "Priya Patel": 90, "Amit Verma": 88 },
    { subject: "Experience", "Rahul Sharma": 90, "Priya Patel": 87, "Amit Verma": 82 },
    { subject: "Growth", "Rahul Sharma": 88, "Priya Patel": 84, "Amit Verma": 86 },
    { subject: "Behavioral", "Rahul Sharma": 85, "Priya Patel": 82, "Amit Verma": 84 }
  ],
  rankingTrend: [
    { rank: "R1", name: "Rahul Sharma", score: 92 },
    { rank: "R2", name: "Priya Patel", score: 89 },
    { rank: "R3", name: "Amit Verma", score: 85 },
    { rank: "R4", name: "Sneha Reddy", score: 82 },
    { rank: "R5", name: "Vikram Malhotra", score: 78 },
    { rank: "R6", name: "Ananya Sen", score: 75 }
  ]
};
