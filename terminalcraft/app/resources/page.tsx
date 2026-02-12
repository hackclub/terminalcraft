import resources from "@/data/resources.json";

type Resource = {
  id: string;
  title: string;
  url: string;
  description: string;
  category: string;
  duration: string;
};

export default function ResourcesPage() {
  return (
    <div className="p-8 min-h-screen bg-[#1E1E1E]">
      <div className="max-w-4xl mx-auto">
        <div className="bg-black rounded-lg border border-[#404040] p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-4 h-4 bg-[#4AF626] rounded-full animate-pulse"></div>
            <h1 className="text-[#4AF626] font-mono text-2xl font-bold">~/resources</h1>
          </div>
          <p className="text-[#808080] font-mono text-sm">
            Beginner guides for shipping your first terminal program.
          </p>
          <p className="text-[#808080] font-mono text-xs mt-2">
            To add or edit links, update <code>data/resources.json</code>.
          </p>
        </div>

        <div className="mt-6 space-y-4">
          {(resources as Resource[]).map((resource) => (
            <article key={resource.id} className="bg-black rounded-lg border border-[#404040] p-5">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <h2 className="text-[#4AF626] font-mono text-lg font-bold">{resource.title}</h2>
                <span className="px-2 py-1 rounded text-xs font-mono bg-[#2D2D2D] text-[#4AF626]">
                  {resource.category}
                </span>
              </div>
              <p className="text-[#808080] font-mono text-sm mt-2">{resource.description}</p>
              <p className="text-[#808080] font-mono text-xs mt-2">
                Estimated time: {resource.duration}
              </p>
              <a
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-3 text-[#4AF626] font-mono text-sm hover:underline"
              >
                Open guide →
              </a>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
