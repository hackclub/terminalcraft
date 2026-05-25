"use client";

import resources from "@/data/resources.json";
import { useState } from "react";

type Resource = {
  id: string;
  title: string;
  url: string;
  description: string;
  category: string;
  duration: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  tags: string[];
};

export default function ResourcesPage() {
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  
  const categories = [
    "All",
    ...new Set((resources as Resource[]).map((r) => r.category)),
  ];

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
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="$ grep resources..."
          className="
            mt-5
            w-full
            bg-[#111111]
            border
            border-[#404040]
            rounded-lg
            px-4
            py-3
            text-[#4AF626]
            font-mono
            text-sm
            outline-none
            focus:border-[#4AF626]
          "
        />
        </div>
        <div className="flex flex-wrap gap-2 mt-4">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`
              px-3 py-1
              text-xs
              font-mono
              border
              rounded
              transition-colors
              ${
                selectedCategory === category
                  ? "bg-[#4AF626] text-black border-[#4AF626]"
                  : "bg-black text-[#808080] border-[#404040] hover:border-[#4AF626]"
              }
            `}
          >
            {category}
          </button>
        ))}
      </div>

        <div className="mt-6 space-y-4">
          {(resources as Resource[])
            .filter((resource) => {
              const q = query.toLowerCase();

              const matchesQuery =
                resource.title.toLowerCase().includes(q) ||
                resource.description.toLowerCase().includes(q) ||
                resource.tags.some((tag) =>
                  tag.toLowerCase().includes(q)
                );

              const matchesCategory =
                selectedCategory === "All" ||
                resource.category === selectedCategory;

              const matchesTag =
                !selectedTag ||
                resource.tags.includes(selectedTag);

              return (
                matchesQuery &&
                matchesCategory &&
                matchesTag
              );
            }).map((resource) => (
                  <article
                    key={resource.id}
                    className="
                      bg-black
                      rounded-lg
                      border
                      border-[#404040]
                      p-5
                      hover:border-[#4AF626]
                      hover:-translate-y-1
                      hover:shadow-[0_0_15px_rgba(74,246,38,0.15)]
                      transition-all
                      duration-200
                    ">
                
            
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <h2 className="text-[#4AF626] font-mono text-lg font-bold">{resource.title}</h2>
                <span className="px-2 py-1 rounded text-xs font-mono bg-[#2D2D2D] text-[#4AF626]">
                  {resource.category}
                </span>
              </div>
              <p className="text-[#808080] font-mono text-sm mt-2">{resource.description}</p>
              
              <div className="flex flex-wrap gap-2 mt-3 text-xs font-mono">
                  <span className="text-[#4AF626]">
                    [{resource.category}]
                  </span>

                  <span className="text-[#808080]">
                    [{resource.duration}]
                  </span>

                  <span className="text-yellow-500">
                    [{resource.difficulty}]
                  </span>
              </div>

              <div className="flex flex-wrap gap-2 mt-3">
                {resource.tags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() =>
                      setSelectedTag(
                        selectedTag === tag ? null : tag
                      )
                    }
                    className={`
                      text-xs
                      font-mono
                      px-2
                      py-1
                      border
                      transition-colors
                      ${
                        selectedTag === tag
                          ? "bg-[#4AF626] text-black border-[#4AF626]"
                          : "bg-[#1A1A1A] text-[#808080] border-[#303030]"
                      }
                    `}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
              <a
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-4 text-[#4AF626] font-mono text-sm hover:underline"
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
