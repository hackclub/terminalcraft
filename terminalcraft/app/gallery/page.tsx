"use client"
import { useState, useEffect, useMemo, useCallback } from 'react'; //funny that DO_NOT_USE_OR_YOU_WILL_BE_FIRED_CALLBACK_REF_RETURN_VALUES is something that exists
import { 
  Rocket, 
  AlertTriangle, 
  X, 
  CheckCircle, 
  ExternalLink, 
  Maximize2, 
  Minimize2, 
  Star, 
  ChevronRight,
  XCircle,
  Github,
  RefreshCw,
  Search
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type Project = {
  id: string;
  name: string;
  description: string;
  author: string;
  language: string;
  stars: number;
  screenshot: string;
};

type ProjectLaunchResponse = {
  success: boolean;
  port?: number;
  url?: string;
  error?: string;
};

type Toast = {
  id: string;
  message: string;
  type: 'success' | 'error';
};

// GitHub API functions
function getGitHubHeaders() {
  const headers: Record<string, string> = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  
  // Add authorization if token is available
  const token = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

async function fetchSubmissions(): Promise<any[]> {
  try {
    console.log('Fetching submissions from GitHub API...');
    const response = await fetch(
      'https://api.github.com/repos/hackclub/terminalcraft/contents/submissions',
      {
        headers: getGitHubHeaders()
      }
    );
    
    console.log('GitHub API response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('GitHub API error response:', errorText);
      
      // Handle rate limiting specifically
      if (response.status === 403 || response.status === 429) {
        throw new Error('GitHub API rate limit exceeded. Please wait and try again.');
      }
      
      throw new Error(`GitHub API error: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('GitHub API response data:', data);
    
    if (!Array.isArray(data)) {
      console.error('Expected array from GitHub API, got:', typeof data, data);
      return [];
    }
    
    const directories = data.filter((item: any) => item.type === 'dir');
    console.log(`Found ${directories.length} directories in submissions folder`);
    return directories;
  } catch (error) {
    console.error('Error fetching submissions:', error);
    return [];
  }
}

async function fetchProjectReadme(projectName: string): Promise<string> {
  try {
    const response = await fetch(
      `https://api.github.com/repos/hackclub/terminalcraft/contents/submissions/${projectName}/README.md`,
      {
        headers: getGitHubHeaders()
      }
    );
    
    if (!response.ok) {
      return '## No description available\n\nREADME.md not found for this project.';
    }
    
    const data = await response.json();
    const content = atob(data.content.replace(/\s/g, ''));
    
    // Return full markdown content for proper rendering
    return content || '## No description available\n\nREADME.md appears to be empty.';
  } catch (error) {
    console.error(`Error fetching README for ${projectName}:`, error);
    return '## Error loading description\n\nFailed to load README.md for this project.';
  }
}

// markdown -> plain text regex func
function markdownToPlainText(markdown: string): string { //thre reason i changed it is cuz i wanna search multiple things not just desc
  return markdown
    .replace(/^#{1,6}\s+/gm, '') // headers
    .replace(/\*{1,2}([^*]+)\*{1,2}/g, '$1') // bold/italic
    .replace(/`([^`]+)`/g, '$1') // inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links, keep text
    .replace(/```[\s\S]*?```/g, '') // code blocks
    .replace(/^\s*[-*+]\s+/gm, '') // list markers
    .replace(/^\s*\d+\.\s+/gm, '') // numbered list markers
    .replace(/\n+/g, ' ') // newlines with spaces
    .trim();
}

async function detectProjectLanguage(projectName: string): Promise<string> {
  try {
    const response = await fetch(
      `https://api.github.com/repos/hackclub/terminalcraft/contents/submissions/${projectName}`,
      {
        headers: getGitHubHeaders()
      }
    );
    
    if (!response.ok) {
      return 'Unknown';
    }
    
    const files = await response.json();
    const fileExtensions: { [key: string]: number } = {};
    
    // Count file extensions and special files
    files.forEach((file: any) => {
      if (file.type === 'file') {
        const fileName = file.name.toLowerCase();
        
        // Handle files with extensions
        if (fileName.includes('.')) {
          const ext = fileName.split('.').pop();
          if (ext) {
            fileExtensions[ext] = (fileExtensions[ext] || 0) + 1;
          }
        } 
        // Handle special files without extensions (common in CLI projects)
        else {
          // Common CLI executable/script names
          const specialFiles: { [key: string]: string } = {
            'makefile': 'makefile',
            'dockerfile': 'docker',
            'cargo': 'cargo',
            'gemfile': 'gemfile',
            'pipfile': 'pipfile',
            'requirements': 'requirements',
            'package': 'package',
            'go.mod': 'go',
            'go.sum': 'go'
          };
          
          if (specialFiles[fileName]) {
            fileExtensions[specialFiles[fileName]] = (fileExtensions[specialFiles[fileName]] || 0) + 1;
          } else if (fileName.length > 0 && !fileName.startsWith('.')) {
            // Likely an executable or script
            fileExtensions['script'] = (fileExtensions['script'] || 0) + 1;
          }
        }
      }
    });
    
    const languageGroups: Record<string, string[]> = {
      JavaScript: ['js', 'mjs', 'cjs', 'jsx'],
      TypeScript: ['ts', 'tsx'],
      Python: ['py', 'py3', 'pyw', 'pyx', 'pyi', 'pipfile', 'requirements'],
      Shell: ['sh', 'zsh', 'fish', 'ksh', 'csh', 'tcsh', 'command'],
      Bash: ['bash'],
      C: ['c', 'h'],
      'C++': ['cpp', 'cxx', 'cc', 'c++', 'hpp', 'hxx', 'hh'],
      Rust: ['rs', 'cargo'],
      Go: ['go'],
      Zig: ['zig'],
      Nim: ['nim'],
      Crystal: ['crystal', 'cr'],
      D: ['d'],
      Java: ['java', 'pom'],
      Kotlin: ['kt', 'kts'],
      Scala: ['scala', 'sc', 'sbt'],
      Clojure: ['clj', 'cljs', 'cljc'],
      Groovy: ['groovy', 'gvy'],
      'C#': ['cs'],
      'F#': ['fs', 'fsx'],
      'VB.NET': ['vb'],
      Ruby: ['rb', 'rbw', 'gemfile'],
      PHP: ['php', 'php3', 'php4', 'php5', 'phtml'],
      Perl: ['pl', 'pm', 'pod'],
      Lua: ['lua'],
      Swift: ['swift'],
      'Objective-C': ['m'],
      'Objective-C++': ['mm'],
      Dart: ['dart'],
      Haskell: ['hs', 'lhs', 'cabal'],
      OCaml: ['ml', 'mli'],
      Elm: ['elm'],
      Elixir: ['ex', 'exs'],
      Erlang: ['erl', 'hrl'],
      R: ['r'],
      Julia: ['jl'],
      V: ['v'],
      Odin: ['odin'],
      Pascal: ['pas', 'pp'],
      Assembly: ['asm', 's', 'nasm'],
      Make: ['makefile'],
      CMake: ['cmake'],
      Gradle: ['gradle'],
      Docker: ['docker', 'dockerfile'],
      Script: ['script'],
      TOML: ['toml'],
      YAML: ['yaml', 'yml'],
      JSON: ['json', 'package'],
      XML: ['xml'],
      Executable: ['exe'],
      Binary: ['bin', 'out'],
      Application: ['app']
    };
    
    // Flatten the language groups into the final language map
    const languageMap: Record<string, string> = {};
    for (const [language, extensions] of Object.entries(languageGroups)) {
      for (const ext of extensions) {
        languageMap[ext.toLowerCase()] = language;
      }
    }
    
    // Find most common language
    let maxCount = 0;
    let mostUsedExt = '';
    
    Object.entries(fileExtensions).forEach(([ext, count]) => {
      if (count > maxCount) {
        maxCount = count;
        mostUsedExt = ext;
      }
    });
    
    return languageMap[mostUsedExt] || 'Unknown';
  } catch (error) {
    console.error(`Error detecting language for ${projectName}:`, error);
    return 'Unknown';
  }
}

// Cache for commit authors to avoid redundant API calls
const authorCache = new Map<string, string>();

async function fetchProjectCommitAuthor(projectName: string): Promise<string> {
  // Check cache first
  if (authorCache.has(projectName)) {
    console.log(`Using cached author for ${projectName}: ${authorCache.get(projectName)}`);
    return authorCache.get(projectName)!;
  }

  try {
    console.log(`Fetching original commit author for project: ${projectName}`);
    
    // Get commits for the specific folder/path (get all to find the first one)
    const response = await fetch(
      `https://api.github.com/repos/hackclub/terminalcraft/commits?path=submissions/${projectName}&per_page=100`,
      {
        headers: getGitHubHeaders()
      }
    );

    if (!response.ok) {
      console.warn(`Failed to get commits for ${projectName}:`, response.status);
      // Try fallback: extract from folder name if API fails
      const nameParts = projectName.split(/[-_]/);
      const fallbackAuthor = nameParts.length > 1 ? nameParts[0] : 'hackclub_user';
      authorCache.set(projectName, fallbackAuthor);
      return fallbackAuthor;
    }

    const commits: any[] = await response.json();
    console.log(`Got ${commits.length} commits for ${projectName}`);

    if (commits.length === 0) {
      console.warn(`No commits found for ${projectName}`);
      // Try fallback: extract from folder name
      const nameParts = projectName.split(/[-_]/);
      const fallbackAuthor = nameParts.length > 1 ? nameParts[0] : 'hackclub_user';
      authorCache.set(projectName, fallbackAuthor);
      return fallbackAuthor;
    }

    // Get the first commit author (original creator) - GitHub API returns newest first, so take the last item
    const firstCommit = commits[commits.length - 1];
    const author = firstCommit.author?.login || firstCommit.commit?.author?.name || 'hackclub_user';
    
    // Clean up the author name (remove email if present)
    const cleanAuthor = author.includes('@') ? author.split('@')[0] : author;
    
    console.log(`Found original author for ${projectName}: ${cleanAuthor} (from first commit)`);
    
    // Cache the result
    authorCache.set(projectName, cleanAuthor);
    return cleanAuthor;
  } catch (error) {
    console.error(`Error fetching commit author for ${projectName}:`, error);
    // Fallback: try to extract from folder name
    const nameParts = projectName.split(/[-_]/);
    const fallbackAuthor = nameParts.length > 1 ? nameParts[0] : 'hackclub_user';
    authorCache.set(projectName, fallbackAuthor);
    return fallbackAuthor;
  }
}

async function loadAllProjectsFromGitHub(): Promise<Project[]> {
  console.log('Loading all projects from GitHub...');
  
  const submissions = await fetchSubmissions();
  console.log(`Got ${submissions.length} submissions from GitHub`);
  
  if (submissions.length === 0) {
    console.warn('No submissions found, returning empty result');
    return [];
  }
  
  const projects: Project[] = [];
  
  console.log(`Processing all ${submissions.length} submissions`);
  
  // Process all submissions in parallel for better performance
  const projectPromises = submissions.map(async (submission) => {
    try {
      console.log(`Processing project: ${submission.name}`);
      
      const [description, language, author] = await Promise.all([
        fetchProjectReadme(submission.name),
        detectProjectLanguage(submission.name),
        fetchProjectCommitAuthor(submission.name)
      ]);
      
      const project: Project = {
        id: submission.sha,
        name: submission.name,
        description: description,
        author: author,
        language: language,
        stars: 0,
        screenshot: `${submission.name} terminal interface`
      };
      
      console.log(`Successfully processed project: ${submission.name}`);
      return project;
    } catch (error) {
      console.error(`Error processing project ${submission.name}:`, error);
      return null;
    }
  });
  
  // Wait for all projects to be processed
  const results = await Promise.all(projectPromises);
  
  // Filter out failed projects
  const successfulProjects = results.filter((project): project is Project => project !== null);
  
  console.log(`Completed processing, returning ${successfulProjects.length} projects`);
  
  return successfulProjects;
}



export default function Gallery() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [launchingProjects, setLaunchingProjects] = useState<Set<string>>(new Set());
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [iframeLoading, setIframeLoading] = useState(false);
  const [iframeError, setIframeError] = useState(false);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState(''); //search query/term new var

  const searchableDescs = useMemo(() => {
    const descs = new Map<string, string>();

    projects.forEach(project => {
      descs.set(project.id, markdownToPlainText(project.description));
    });

    return descs;
  }, [projects]);

  const getProjectSummary = useCallback(
    (project: Project, maxLength: number = 150) => { //type checking is killing me
      const plainDesc = searchableDescs.get(project.id) ?? markdownToPlainText(project.description);

      return plainDesc.length > maxLength
        ? `${plainDesc.slice(0, maxLength)}...`
        : plainDesc;
    },
    [searchableDescs]
  );

  const filteredProjs = useMemo(() => {
    if (!searchQuery.trim()) {
      return projects;
    }

    const normSearch = searchQuery.trim().toLowerCase();

    return projects.filter((project) => {
      const plainDesc = (searchableDescs.get(project.id) ?? markdownToPlainText(project.description)).toLowerCase();

      return (
        project.name.toLowerCase().includes(normSearch) ||
        project.author.toLowerCase().includes(normSearch) ||
        project.language.toLowerCase().includes(normSearch) ||
        plainDesc.includes(normSearch)
      );
    });
  }, [projects, searchQuery, searchableDescs]);

  // Toast management
  const addToast = (message: string, type: 'success' | 'error') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  // Preview management
  const closeModal = () => {
    setSelectedProject(null);
    setPreviewUrl(null);
    setIsFullscreen(false);
    setIframeLoading(false);
    setIframeError(false);
    setIsDescriptionExpanded(false);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const openInNewTab = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  };

  // Launch project function
  const launchProject = async (projectName: string) => {
    if (launchingProjects.has(projectName)) return;

    setLaunchingProjects(prev => new Set(prev).add(projectName));

    try {
      const response = await fetch(`https://terminalcraft.josiasw.dev/projects/${projectName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ProjectLaunchResponse = await response.json();

      if (data.success && data.url) {
        addToast(`${projectName} launched successfully!`, 'success');
        // Set the preview URL to load in iframe
        setIframeLoading(true);
        setIframeError(false);
        setPreviewUrl(`https://${data.url}`);
      } else {
        throw new Error(data.error || 'Failed to launch project');
      }
    } catch (err) {
      console.error('Error launching project:', err);
      addToast(`Failed to launch ${projectName}. Please try again.`, 'error');
    } finally {
      setLaunchingProjects(prev => {
        const newSet = new Set(prev);
        newSet.delete(projectName);
        return newSet;
      });
    }
  };

  // Load all projects
  const loadAllProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Starting to load all projects...');
      
      const allProjects = await loadAllProjectsFromGitHub();
      console.log('Load projects result:', allProjects);
      
      setProjects(allProjects);
      
      if (allProjects.length === 0) {
        setError('No projects found in submissions folder. This might be a temporary GitHub API issue.');
      }
    } catch (err) {
      console.error('Error loading projects:', err);
      setError(`Failed to load projects: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }

    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [selectedProject]);

  // Keyboard support for modal
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && selectedProject) {
        closeModal();
      }
      // Toggle description expansion with 'D' key
      if (event.key === 'd' || event.key === 'D') {
        if (selectedProject && selectedProject.description.length > 500) {
          const wasExpanded = isDescriptionExpanded;
          setIsDescriptionExpanded(!isDescriptionExpanded);
          // Scroll to top when expanding
          if (!wasExpanded) {
            setTimeout(() => {
              const descriptionEl = document.querySelector('.description-content');
              if (descriptionEl) {
                descriptionEl.scrollTo({ top: 0, behavior: 'smooth' });
              }
            }, 100);
          }
        }
      }
    };

    if (selectedProject) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [selectedProject, isDescriptionExpanded]);

  if (loading) {
    return (
      <div className="p-8 min-h-screen bg-[#1E1E1E] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[#4AF626] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#4AF626] font-mono">Loading projects from GitHub...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 min-h-screen bg-[#1E1E1E] flex items-center justify-center">
        <div className="max-w-2xl text-center">
          <div className="bg-black border border-red-500 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <h2 className="text-red-500 font-mono text-xl font-bold">Connection Error</h2>
            </div>
            <p className="text-red-500 font-mono text-sm mb-4">{error}</p>
            <div className="text-[#808080] font-mono text-xs mb-4">
              <p>Possible causes:</p>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>GitHub API rate limit exceeded</li>
                <li>Network connectivity issues</li>
                <li>Repository access restrictions</li>
                <li>Temporary GitHub service outage</li>
              </ul>
            </div>
          </div>
          
          <div className="space-y-3">
            <button 
              onClick={loadAllProjects}
              disabled={loading}
              className="bg-[#4AF626] text-black font-mono text-sm font-bold py-2 px-6 rounded hover:bg-[#3FE01F] transition-colors duration-200 disabled:opacity-50"
            >
              {loading ? 'Retrying...' : 'Retry Loading Projects'}
            </button>
            
            <div className="text-[#808080] font-mono text-xs">
              <p>Check the browser console (F12) for detailed error logs</p>
            </div>
            
            <button 
              onClick={() => window.open('https://github.com/hackclub/terminalcraft/tree/main/submissions', '_blank')}
              className="block mx-auto text-[#4AF626] font-mono text-sm hover:underline"
            >
              View submissions folder on GitHub →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 min-h-screen bg-[#1E1E1E]">
      <div className="max-w-6xl mx-auto">
        {/* Gallery Header */}
        <div className="mb-8">
          <div className="bg-black rounded-lg p-6 border border-[#404040]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-4 h-4 bg-[#4AF626] rounded-full animate-pulse"></div>
              <h1 className="text-[#4AF626] font-mono text-2xl font-bold">
                ~/gallery
              </h1>
            </div>
            <p className="text-[#808080] font-mono text-sm">
              user@hackclub:~/gallery$ ls -la
            </p>
            <p className="text-[#4AF626] font-mono text-sm mt-2">
              Discover amazing terminal applications built by the community
            </p>
            <div className="mt-2">
              <p className="text-[#808080] font-mono text-xs">
                Loaded {projects.length} projects from hackclub/terminalcraft/submissions by original creators
              </p>
              <p className="text-[#808080] font-mono text-xs mt-1">
                Showing {filteredProjs.length} project{filteredProjs.length === 1 ? '' : 's'} 
              </p> {/*<!-- im so proud of myself i figured it out i hate the triple equality bs -->*/}
            </div>
            <div className="mt-4">
              <label htmlFor="gallery-search" className="relative block">
                <Search
                  aria-hidden="true"
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#808080]"
                />
                <input
                  id="gallery-search"
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search projects by name, author, language, or description..."
                  aria-label='Search submissions'
                  className="w-full bg-[#0f0f0f] border border-[#404040] rounded-md py-2 pl-10 pr-4 text-[#4AF626] placeholder:text-[#404040] font-mono text-sm focus:outline-none focus:border-[#4AF626] focus:ring-1 focus:ring-[#4AF626]"
                />
              </label>
            </div>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjs.map((project) => (
            <div
              key={project.id}
              className={`bg-black rounded-lg border overflow-hidden transition-all duration-300 cursor-pointer ${
                launchingProjects.has(project.name)
                  ? 'border-[#4AF626] shadow-lg shadow-[#4AF626]/20'
                  : 'border-[#404040] hover:border-[#4AF626]'
              }`}
              onClick={() => setSelectedProject(project)}
            >
              {/* Project Header */}
              <div className="p-4 border-b border-[#404040]">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-[#4AF626] font-mono font-bold text-lg flex items-center gap-2">
                    {project.name}
                    {launchingProjects.has(project.name) && (
                      <div className="w-4 h-4 border-2 border-[#4AF626] border-t-transparent rounded-full animate-spin"></div>
                    )}
                  </h3>
                  <div className="flex items-center gap-2">
                    <Star className="w-3 h-3 text-[#808080]" />
                    <span className="text-[#808080] font-mono text-xs">{project.stars}</span>
                  </div>
                </div>
                <p className="text-[#808080] font-mono text-xs mb-2">
                  by {project.author}
                </p>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-[#2D2D2D] text-[#4AF626] font-mono text-xs rounded">
                    {project.language}
                  </span>
                </div>
              </div>

              {/* Project Content */}
              <div className="p-4">
                <p className="text-[#808080] font-mono text-sm mb-4 line-clamp-3">
                  {getProjectSummary(project)}
                </p>
                
                {/* Try Now Button */}
                <div className="space-y-2">
                                    <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedProject(project);
                      // Auto-launch the project preview when opening modal from button
                      setTimeout(() => {
                        launchProject(project.name);
                      }, 300); // Small delay to let modal render
                    }}
                    disabled={launchingProjects.has(project.name)}
                    className={`w-full font-mono text-sm font-bold py-2 px-4 rounded transition-all duration-200 ${
                      launchingProjects.has(project.name)
                        ? 'bg-[#808080] text-[#404040] cursor-not-allowed'
                        : 'bg-[#4AF626] text-black hover:bg-[#3FE01F]'
                    }`}
                  >
                    {launchingProjects.has(project.name) ? (
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-[#404040] border-t-transparent rounded-full animate-spin"></div>
                        Launching...
                      </div>
                    ) : (
                                              <span className="flex items-center gap-2">
                          <Rocket className="w-4 h-4" />
                          Launch
                        </span>
                    )}
                  </button>
                </div>
              </div>

              {/* Project Footer */}
              <div className="p-4 border-t border-[#404040]">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-[#808080]">click to view details</span>
                  <ChevronRight className="w-4 h-4 text-[#4AF626]" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {projects.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-[#808080] font-mono">No projects found in submissions folder</p>
          </div>
        )}

        {projects.length > 0 && filteredProjs.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-[#808080] font-mono">No projects match your search criteria</p>
          </div>
        )}

        {/* Project Modal */}
        {selectedProject && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-2 sm:p-4 z-50"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                closeModal();
              }
            }}
          >
            <div className={`bg-black border border-[#4AF626] rounded-lg w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto animate-modal-in ${
              previewUrl ? 'max-w-7xl' : 'max-w-5xl'
            }`}>
              {/* Modal Header */}
              <div className="p-4 sm:p-6 border-b border-[#404040]">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-[#4AF626] font-mono text-xl sm:text-2xl font-bold truncate pr-2">
                    {selectedProject.name}
                  </h2>
                  <button
                    onClick={closeModal}
                    className="text-[#808080] hover:text-[#4AF626] p-2 rounded hover:bg-[#404040] transition-colors flex-shrink-0"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                {/* Mobile-first responsive layout */}
                <div className="space-y-3 sm:space-y-2">
                  {/* Project info - stack on mobile */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm font-mono">
                      <span className="text-[#808080]">
                        Author: 
                        <a 
                          href={`https://github.com/${selectedProject.author}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#4AF626] hover:underline ml-1"
                        >
                          @{selectedProject.author}
                        </a>
                      </span>
                      <div className="flex items-center gap-4">
                        <span className="text-[#808080]">Language: {selectedProject.language}</span>
                        <span className="text-[#808080] flex items-center gap-1">
                          <Star className="w-3 h-3" />
                          {selectedProject.stars}
                        </span>
                      </div>
                    </div>
                    
                    {/* Keyboard shortcuts - hide on small mobile */}
                    <div className="text-[#808080] font-mono text-xs hidden sm:block">
                      <span className="opacity-70">ESC to close</span>
                      {selectedProject.description.length > 500 && (
                        <span className="opacity-70 ml-2">• D to expand</span>
                      )}
                    </div>
                  </div>
                  
                  {/* GitHub link */}
                  <div>
                    <a 
                      href={`https://github.com/hackclub/terminalcraft/tree/main/submissions/${selectedProject.name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#4AF626] font-mono text-sm hover:underline"
                    >
                      View on GitHub →
                    </a>
                  </div>
                </div>
              </div>

              {/* Modal Content */}
              <div className="p-4 sm:p-6">
                {!previewUrl ? (
                  // Description view (before launching)
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                    {/* Description */}
                    <div>
                                          <div className="flex items-center justify-between mb-3">
                      <h3 className="text-[#4AF626] font-mono font-bold">Description</h3>
                      {selectedProject.description.length > 500 && (
                        <button
                          onClick={() => {
                            setIsDescriptionExpanded(!isDescriptionExpanded);
                            // Scroll to top of description when expanding
                            if (!isDescriptionExpanded) {
                              setTimeout(() => {
                                const descriptionEl = document.querySelector('.description-content');
                                if (descriptionEl) {
                                  descriptionEl.scrollTo({ top: 0, behavior: 'smooth' });
                                }
                              }, 100);
                            }
                          }}
                          className={`font-mono text-xs px-3 py-1 rounded transition-colors flex items-center gap-1 ${
                            isDescriptionExpanded 
                              ? 'text-[#808080] hover:text-[#4AF626] hover:bg-[#404040]' 
                              : 'text-[#4AF626] bg-[#404040] hover:bg-[#4AF626] hover:text-black'
                          }`}
                          title={`${isDescriptionExpanded ? 'Collapse' : 'Expand'} description (Press D)`}
                        >
                          {isDescriptionExpanded ? (
                            <>
                              <Minimize2 className="w-3 h-3" />
                              Show Less
                            </>
                          ) : (
                            <>
                              <Maximize2 className="w-3 h-3" />
                              Show Full README
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    <div className={`description-content relative text-[#808080] font-mono text-sm mb-6 prose prose-invert prose-sm max-w-none transition-all duration-300 ${
                      isDescriptionExpanded ? 'max-h-none overflow-y-auto' : 'max-h-32 overflow-y-auto'
                    }`}>
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // Custom components for terminal styling
                          h1: ({children}) => <h1 className="text-[#4AF626] font-mono font-bold text-lg mb-3">{children}</h1>,
                          h2: ({children}) => <h2 className="text-[#4AF626] font-mono font-bold text-base mb-2">{children}</h2>,
                          h3: ({children}) => <h3 className="text-[#4AF626] font-mono font-bold text-sm mb-2">{children}</h3>,
                          p: ({children}) => <p className="text-[#808080] font-mono text-sm mb-3 leading-relaxed">{children}</p>,
                          code: ({children}) => <code className="bg-black text-[#4AF626] px-1 py-0.5 rounded font-mono text-xs">{children}</code>,
                          pre: ({children}) => <pre className="bg-black border border-[#404040] rounded p-3 mb-3 overflow-x-auto">{children}</pre>,
                          ul: ({children}) => <ul className="text-[#808080] font-mono text-sm mb-3 ml-4">{children}</ul>,
                          ol: ({children}) => <ol className="text-[#808080] font-mono text-sm mb-3 ml-4">{children}</ol>,
                          li: ({children}) => <li className="mb-1 list-disc">{children}</li>,
                          a: ({href, children}) => <a href={href} className="text-[#4AF626] hover:underline" target="_blank" rel="noopener noreferrer">{children}</a>,
                          blockquote: ({children}) => <blockquote className="border-l-2 border-[#4AF626] pl-3 ml-2 text-[#808080] italic">{children}</blockquote>
                        }}
                      >
                        {isDescriptionExpanded ? selectedProject.description : getProjectSummary(selectedProject, 500)}
                      </ReactMarkdown>
                      {!isDescriptionExpanded && selectedProject.description.length > 500 && (
                        <div className="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-[#1E1E1E] to-transparent pointer-events-none"></div>
                      )}
                    </div>

                      {/* Try Now Section */}
                      <h3 className="text-[#4AF626] font-mono font-bold mb-3">Live Demo</h3>
                      <div className="space-y-3">
                                              <button
                        onClick={() => launchProject(selectedProject.name)}
                        disabled={launchingProjects.has(selectedProject.name) || previewUrl !== null}
                        className={`w-full font-mono text-sm font-bold py-3 px-4 sm:px-6 rounded transition-all duration-200 ${
                          launchingProjects.has(selectedProject.name) || previewUrl !== null
                            ? 'bg-[#808080] text-[#404040] cursor-not-allowed'
                            : 'bg-[#4AF626] text-black hover:bg-[#3FE01F]'
                        }`}
                      >
                                                  {launchingProjects.has(selectedProject.name) ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-5 h-5 border-2 border-[#404040] border-t-transparent rounded-full animate-spin"></div>
                            Launching {selectedProject.name}...
                          </div>
                        ) : previewUrl ? (
                          <span className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
                            Preview Active
                          </span>
                        ) : (
                          <span className="flex items-center gap-2">
                            <Rocket className="w-4 h-4" />
                            Try Now
                          </span>
                        )}
                      </button>
                      <div className="bg-[#2D2D2D] p-3 rounded font-mono text-xs">
                        <span className="text-[#808080]">Status: </span>
                        <span className="text-[#4AF626]">
                          {launchingProjects.has(selectedProject.name) 
                            ? 'Launching project...' 
                            : previewUrl 
                              ? 'Preview loaded' 
                              : 'Ready to launch'
                          }
                        </span>
                      </div>
                      </div>
                    </div>

                    {/* Placeholder Preview */}
                    <div>
                      <h3 className="text-[#4AF626] font-mono font-bold mb-3">Preview</h3>
                      <div className="bg-[#2D2D2D] p-4 rounded border border-[#404040]">
                        <div className="bg-black p-4 rounded font-mono text-xs">
                          <div className="text-[#4AF626] mb-2">
                            {selectedProject.name} v1.0.0
                          </div>
                          <div className="text-[#808080] mb-2">
                            ╭─────────────────────────────────────╮
                          </div>
                          <div className="text-[#808080] mb-2">
                            │ {selectedProject.description.slice(0, 35)}... │
                          </div>
                          <div className="text-[#808080] mb-2">
                            ╰─────────────────────────────────────╯
                          </div>
                          <div className="text-[#4AF626]">
                            Click "Try Now" to start the live preview →
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Preview view (after launching)
                  <div className="space-y-4">
                    {/* Preview Controls */}
                    <div className="bg-[#2D2D2D] p-3 rounded border border-[#404040]">
                      {/* Top row - Live Preview indicator */}
                      <div className="flex items-center justify-between mb-3 sm:mb-0">
                        <div className="flex items-center gap-2 sm:gap-4">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-[#4AF626] rounded-full animate-pulse"></div>
                            <span className="text-[#4AF626] font-mono text-sm font-bold">
                              Live Preview
                            </span>
                          </div>
                          <span className="text-[#808080] font-mono text-xs hidden sm:inline">
                            {selectedProject.name}
                          </span>
                        </div>
                        
                        {/* Mobile: Close button only, Desktop: All controls */}
                        <div className="sm:hidden">
                          <button
                            onClick={() => {
                              setPreviewUrl(null);
                              setIframeLoading(false);
                              setIframeError(false);
                            }}
                            className="text-[#808080] hover:text-red-500 font-mono text-xs px-3 py-2 rounded hover:bg-[#404040] transition-colors flex items-center gap-2"
                            title="Close preview"
                          >
                            <X className="w-4 h-4" />
                            Close
                          </button>
                        </div>
                      </div>

                      {/* Desktop controls */}
                      <div className="hidden sm:flex items-center justify-end gap-2">
                        <button
                          onClick={openInNewTab}
                          className="text-[#808080] hover:text-[#4AF626] font-mono text-xs px-2 py-1 rounded hover:bg-[#404040] transition-colors flex items-center gap-1"
                          title="Open in new tab"
                        >
                          <ExternalLink className="w-3 h-3" />
                          New Tab
                        </button>
                        <button
                          onClick={toggleFullscreen}
                          className="text-[#808080] hover:text-[#4AF626] font-mono text-xs px-2 py-1 rounded hover:bg-[#404040] transition-colors flex items-center gap-1"
                          title="Toggle fullscreen"
                        >
                          {isFullscreen ? (
                            <>
                              <Minimize2 className="w-3 h-3" />
                              Exit
                            </>
                          ) : (
                            <>
                              <Maximize2 className="w-3 h-3" />
                              Full
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setPreviewUrl(null);
                            setIframeLoading(false);
                            setIframeError(false);
                          }}
                          className="text-[#808080] hover:text-red-500 font-mono text-xs px-2 py-1 rounded hover:bg-[#404040] transition-colors flex items-center gap-1"
                          title="Close preview"
                        >
                          <X className="w-3 h-3" />
                          Close
                        </button>
                      </div>

                      {/* Mobile controls row */}
                      <div className="flex sm:hidden items-center justify-center gap-2 pt-2 border-t border-[#404040]">
                        <button
                          onClick={openInNewTab}
                          className="text-[#808080] hover:text-[#4AF626] font-mono text-xs px-3 py-2 rounded hover:bg-[#404040] transition-colors flex items-center gap-2 flex-1 justify-center"
                          title="Open in new tab"
                        >
                          <ExternalLink className="w-4 h-4" />
                          New Tab
                        </button>
                        <button
                          onClick={toggleFullscreen}
                          className="text-[#808080] hover:text-[#4AF626] font-mono text-xs px-3 py-2 rounded hover:bg-[#404040] transition-colors flex items-center gap-2 flex-1 justify-center"
                          title="Toggle fullscreen"
                        >
                          {isFullscreen ? (
                            <>
                              <Minimize2 className="w-4 h-4" />
                              Exit Full
                            </>
                          ) : (
                            <>
                              <Maximize2 className="w-4 h-4" />
                              Fullscreen
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Live Preview Iframe */}
                    <div className="relative">
                      <iframe
                        src={previewUrl}
                        className={`w-full bg-white rounded border border-[#404040] overflow-hidden ${
                          isFullscreen ? 'h-[60vh] sm:h-[70vh]' : 'h-[40vh] sm:h-[50vh]'
                        }`}
                        style={{ overflow: 'hidden' }}
                        title={`${selectedProject.name} Live Preview`}
                        allow="clipboard-read; clipboard-write"
                        sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
                        onLoad={() => setIframeLoading(false)}
                        onError={() => {
                          setIframeLoading(false);
                          setIframeError(true);
                        }}
                      />
                      {/* Loading overlay */}
                      {iframeLoading && (
                        <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center rounded">
                          <div className="text-center">
                            <div className="w-8 h-8 border-2 border-[#4AF626] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                            <p className="text-[#4AF626] font-mono text-sm">Loading preview...</p>
                          </div>
                        </div>
                      )}
                      
                      {/* Error overlay */}
                      {iframeError && (
                        <div className="absolute inset-0 bg-black bg-opacity-90 flex items-center justify-center rounded p-2">
                          <div className="text-center max-w-md p-4">
                            <AlertTriangle className="w-8 h-8 sm:w-12 sm:h-12 text-red-500 mx-auto mb-4" />
                            <h4 className="text-red-500 font-mono font-bold mb-2 text-sm sm:text-base">Preview Error</h4>
                            <p className="text-[#808080] font-mono text-xs sm:text-sm mb-4">
                              The project preview couldn't be loaded. This might be due to:
                            </p>
                            <ul className="text-[#808080] font-mono text-xs mb-4 text-left">
                              <li>• The project is still starting up</li>
                              <li>• Network connectivity issues</li>
                              <li>• Project configuration problems</li>
                            </ul>
                            <div className="flex flex-col sm:flex-row gap-2 sm:space-x-2 sm:gap-0">
                              <button
                                onClick={openInNewTab}
                                className="bg-[#4AF626] text-black font-mono text-xs px-3 py-2 rounded hover:bg-[#3FE01F] transition-colors"
                              >
                                Open in New Tab
                              </button>
                              <button
                                onClick={() => {
                                  setIframeError(false);
                                  setIframeLoading(true);
                                  // Force reload iframe
                                  const iframe = document.querySelector('iframe');
                                  if (iframe && previewUrl) {
                                    iframe.src = previewUrl;
                                  }
                                }}
                                className="bg-[#808080] text-black font-mono text-xs px-3 py-2 rounded hover:bg-[#606060] transition-colors"
                              >
                                Retry
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Project Info */}
                    <div className="bg-[#2D2D2D] p-4 rounded border border-[#404040]">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-[#4AF626] font-mono font-bold">About this project</h4>
                        {selectedProject.description.length > 300 && (
                          <button
                            onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                            className="text-[#808080] hover:text-[#4AF626] font-mono text-xs px-2 py-1 rounded hover:bg-[#404040] transition-colors flex items-center gap-1"
                          >
                            {isDescriptionExpanded ? (
                              <>
                                <Minimize2 className="w-2 h-2" />
                                Less
                              </>
                            ) : (
                              <>
                                <Maximize2 className="w-2 h-2" />
                                More
                              </>
                            )}
                          </button>
                        )}
                      </div>
                                             <div className={`relative text-[#808080] font-mono text-sm mb-3 transition-all duration-300 ${
                         isDescriptionExpanded ? 'max-h-none' : 'max-h-32 overflow-y-auto'
                       }`}>
                         <ReactMarkdown 
                           remarkPlugins={[remarkGfm]}
                           components={{
                             // Compact styling for the preview section
                             h1: ({children}) => <h1 className="text-[#4AF626] font-mono font-bold text-sm mb-2">{children}</h1>,
                             h2: ({children}) => <h2 className="text-[#4AF626] font-mono font-bold text-xs mb-1">{children}</h2>,
                             h3: ({children}) => <h3 className="text-[#4AF626] font-mono font-bold text-xs mb-1">{children}</h3>,
                             p: ({children}) => <p className="text-[#808080] font-mono text-xs mb-2 leading-relaxed">{children}</p>,
                             code: ({children}) => <code className="bg-black text-[#4AF626] px-1 py-0.5 rounded font-mono text-xs">{children}</code>,
                             ul: ({children}) => <ul className="text-[#808080] font-mono text-xs mb-2 ml-3">{children}</ul>,
                             ol: ({children}) => <ol className="text-[#808080] font-mono text-xs mb-2 ml-3">{children}</ol>,
                             li: ({children}) => <li className="mb-1 list-disc">{children}</li>,
                             a: ({href, children}) => <a href={href} className="text-[#4AF626] hover:underline" target="_blank" rel="noopener noreferrer">{children}</a>
                           }}
                         >
                           {isDescriptionExpanded ? selectedProject.description : getProjectSummary(selectedProject, 300)}
                         </ReactMarkdown>
                         {!isDescriptionExpanded && selectedProject.description.length > 300 && (
                           <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-[#2D2D2D] to-transparent pointer-events-none"></div>
                         )}
                       </div>
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs font-mono">
                        <span className="text-[#808080]">Language: {selectedProject.language}</span>
                        <span className="text-[#808080]">
                          Author: 
                          <a 
                            href={`https://github.com/${selectedProject.author}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#4AF626] hover:underline ml-1"
                          >
                            @{selectedProject.author}
                          </a>
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Toast Notifications */}
        <div className="fixed top-4 right-2 sm:right-4 z-50 space-y-2 w-auto max-w-[calc(100vw-1rem)] sm:max-w-96">
          {toasts.map((toast) => (
            <div
              key={toast.id}
              className={`
                min-w-72 sm:min-w-80 max-w-full p-3 sm:p-4 rounded-lg border font-mono text-xs sm:text-sm
                transform transition-all duration-300 ease-in-out
                ${toast.type === 'success' 
                  ? 'bg-black border-[#4AF626] text-[#4AF626]' 
                  : 'bg-black border-red-500 text-red-500'
                }
                animate-slide-in-right
              `}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {toast.type === 'success' ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <XCircle className="w-4 h-4" />
                  )}
                  <span>{toast.message}</span>
                </div>
                <button
                  onClick={() => removeToast(toast.id)}
                  className="ml-2 text-[#808080] hover:text-white transition-colors p-1 sm:p-1 rounded hover:bg-[#404040] flex-shrink-0"
                >
                  <X className="w-3 h-3 sm:w-4 sm:h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
