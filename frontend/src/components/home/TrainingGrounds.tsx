import { ArrowRight, BookOpen, Target, Award, BookMarked } from 'lucide-react';

const TrainingGrounds = () => {
  const learningPaths = [
    {
      id: 1,
      title: 'Career Clarity 101',
      description: 'Discover your strengths and explore career directions.',
      icon: <BookOpen className="w-6 h-6 text-primary" />,
      progress: 65,
      lessons: 24,
      color: 'bg-sky-100',
      borderColor: 'border-sky-200',
      textColor: 'text-primary',
    },
    {
      id: 2,
      title: 'Focus & Productivity',
      description: 'Learn how to manage distractions and study effectively.',
      icon: <Target className="w-6 h-6 text-primary" />,
      progress: 30,
      lessons: 18,
      color: 'bg-sky-100',
      borderColor: 'border-sky-200',
      textColor: 'text-primary',
    },
    {
      id: 3,
      title: 'Emotional Balance',
      description: 'Build resilience and handle stress with calm.',
      icon: <Award className="w-6 h-6 text-primary" />,
      progress: 45,
      lessons: 32,
      color: 'bg-sky-100',
      borderColor: 'border-sky-200',
      textColor: 'text-primary',
    },
    {
      id: 4,
      title: 'Decision Making Skills',
      description: 'Practice making confident choices in life and academics.',
      icon: <BookMarked className="w-6 h-6 text-primary" />,
      progress: 20,
      lessons: 15,
      color: 'bg-sky-100',
      borderColor: 'border-sky-200',
      textColor: 'text-primary',
    },
  ];

  return (
    <section className="py-16 bg-gradient-to-b from-sky-50 to-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-serif font-bold text-ink mb-4">CLASSROOM's</h2>
          <p className="text-muted max-w-2xl mx-auto">
            Continue your journey through sacred knowledge and self-discovery
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {learningPaths.map((path) => (
            <div 
              key={path.id}
              className={`bg-white rounded-xl shadow-sm border ${path.borderColor} overflow-hidden hover:shadow-md transition-shadow duration-300`}
            >
              <div className="p-6">
                <div className={`w-12 h-12 ${path.color} rounded-lg flex items-center justify-center mb-4`}>
                  {path.icon}
                </div>
                <h3 className="text-lg font-medium text-ink mb-1">{path.title}</h3>
                <p className="text-sm text-muted mb-4">{path.description}</p>
                
                <div className="mb-3">
                  <div className="flex justify-between text-xs text-muted mb-1">
                    <span>Progress</span>
                    <span>{path.progress}%</span>
                  </div>
                  <div className="w-full bg-sky-100 rounded-full h-2">
                    <div 
                      className={`h-full rounded-full ${path.color.replace('bg-', 'bg-opacity-80 ')}`}
                      style={{ width: `${path.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted">{path.lessons} lessons</span>
                  <button 
                    className={`flex items-center ${path.textColor} font-medium hover:underline`}
                  >
                    Continue <ArrowRight className="ml-1 w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <p className="text-center text-sm text-muted mt-6">
          In the future, your student-created classrooms will appear here as your learning history.
        </p>

        <div className="mt-12 text-center">
          <button className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full text-white bg-primary hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors duration-200">
            Explore All Paths
          </button>
        </div>
      </div>
    </section>
  );
};

export default TrainingGrounds;
