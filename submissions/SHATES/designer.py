#!/usr/bin/env python3

import click
import requests
import random
import json
import os
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
import webbrowser
import textwrap

console = Console()
COLOR_SCHEMES = {
    "primary": "bright_blue",
    "secondary": "bright_cyan", 
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "accent": "bright_magenta"
}

FONT_CATEGORIES = {
    "classic": [
        "Times New Roman", "Georgia", "Garamond", "Baskerville", 
        "Minion Pro", "Caslon", "Trajan Pro", "Optima"
    ],
    "modern": [
        "Helvetica", "Arial", "Futura", "Avenir", "Proxima Nova", 
        "Gotham", "Montserrat", "Lato", "Open Sans", "Source Sans Pro"
    ],
    "playful": [
        "Comic Sans MS", "Lobster", "Pacifico", "Fredoka One", 
        "Bubblegum Sans", "Quicksand", "Nunito", "Raleway", "Poppins"
    ],
    "elegant": [
        "Playfair Display", "Crimson Text", "Libre Baskerville",
        "Cormorant Garamond", "EB Garamond", "Merriweather"
    ],
    "tech": [
        "JetBrains Mono", "Fira Code", "Source Code Pro", "Monaco",
        "Consolas", "Ubuntu Mono", "Roboto Mono", "Space Mono"
    ]
}

GOOGLE_FONTS = {
    "classic": [
        "Playfair Display", "Crimson Text", "Libre Baskerville", 
        "Cormorant Garamond", "EB Garamond", "Merriweather"
    ],
    "modern": [
        "Inter", "Roboto", "Open Sans", "Lato", "Montserrat", 
        "Source Sans Pro", "Nunito Sans", "Work Sans"
    ],
    "playful": [
        "Pacifico", "Lobster", "Dancing Script", "Kalam", 
        "Fredoka One", "Righteous", "Comfortaa", "Caveat"
    ],
    "elegant": [
        "Playfair Display", "Cormorant Garamond", "Crimson Text",
        "Libre Baskerville", "EB Garamond", "Spectral"
    ],
    "tech": [
        "JetBrains Mono", "Fira Code", "Source Code Pro", 
        "Ubuntu Mono", "Roboto Mono", "Space Mono"
    ]
}

DESIGN_TIPS = [
    "🎨 Use the 60-30-10 rule for color distribution in your designs",
    "📏 Maintain consistent spacing using a baseline grid (8px or 4px)",
    "🔤 Limit yourself to 2-3 font families per project",
    "⚖️ Create visual hierarchy using size, weight, and spacing",
    "🎯 Always design with your target audience in mind",
    "📱 Design mobile-first, then scale up to desktop",
    "🔍 Ensure sufficient color contrast for accessibility (4.5:1 ratio)",
    "🎭 Use whitespace effectively - it's not empty space, it's breathing room",
    "🌈 Colors have psychological impact - choose them intentionally",
    "📐 Follow the rule of thirds for better composition",
    "🎪 Less is more - avoid cluttering your designs",
    "🔄 Maintain consistency across all design elements",
    "👁️ Test your designs with real users whenever possible",
    "📊 Use data to inform your design decisions",
    "🎨 Create a style guide to maintain brand consistency",
    "✨ Use micro-interactions to enhance user experience",
    "🎬 Motion design should have purpose, not just decoration",
    "🔗 Group related elements using proximity and similarity",
    "🎪 Create visual interest with asymmetrical balance",
    "🌟 Make your call-to-action buttons stand out with contrasting colors"
]

class AIAssistant:
    def __init__(self):
        self.api_url = "https://ai.hackclub.com/chat/completions"
        
    def get_design_advice(self, prompt: str) -> str:
        """Get design advice from AI assistant"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("🤖 Getting AI advice...", start=False)
                
                design_context = """You are a professional design consultant and creative director with 15+ years of experience. 
                Provide practical, actionable design advice. Be concise but thorough. Use emojis sparingly and professionally.
                Focus on: visual hierarchy, color theory, typography, user experience, branding, and design principles."""
                
                messages = [
                    {"role": "system", "content": design_context},
                    {"role": "user", "content": f"Design question: {prompt}"}
                ]
                
                response = requests.post(
                    self.api_url,
                    json={"messages": messages, "max_tokens": 500},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    return f"Sorry, I couldn't process your request. Status: {response.status_code}"
                    
        except Exception as e:
            return f"AI assistant temporarily unavailable: {str(e)}"
    
    def analyze_color_palette(self, colors: List[str]) -> str:
        """Analyze color palette with AI"""
        colors_str = ", ".join(colors)
        prompt = f"Analyze this color palette for design use: {colors_str}. Comment on harmony, psychology, use cases, and potential improvements."
        return self.get_design_advice(prompt)
    
    def suggest_font_pairing(self, primary_font: str, design_type: str = "general") -> str:
        """Get font pairing suggestions"""
        prompt = f"Suggest 3 fonts that pair well with {primary_font} for {design_type} design. Explain why each pairing works."
        return self.get_design_advice(prompt)

class DesignerCLI:
    def __init__(self):
        self.console = Console()
        self.ai = AIAssistant()

    def show_welcome_banner(self):
        """Display beautiful welcome banner"""
        banner_text = """
╔══════════════════════════════════════════════════════╗
║                  🎨 DESIGNER CLI                     ║
║              Your Creative Companion                 ║
║         ────────────────────────────────────         ║
║  ✨ Palettes  🔤 Fonts  🏷️ Logos  🤖 AI Assistant   ║
╚══════════════════════════════════════════════════════╝
        """
        console.print(Panel.fit(
            banner_text,
            style=f"bold {COLOR_SCHEMES['primary']}",
            border_style=COLOR_SCHEMES['accent']
        ))

    def generate_color_palette(self, count: int = 5, search_query: str = None) -> List[str]:
        """Generate color palette using ColorMagic API or fallback to random"""
        if search_query:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    task = progress.add_task(f"🎨 Searching for '{search_query}' palettes...", start=False)
                    
                    response = requests.get(
                        f"https://colormagic.app/api/palette/search?q={search_query}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            palette = data[0]
                            if 'colors' in palette:
                                colors = [f"#{color}" if not color.startswith('#') else color 
                                        for color in palette['colors'][:count]]
                                return colors
            except Exception as e:
                console.print(f"[{COLOR_SCHEMES['warning']}]🌐 API unavailable, generating random colors...[/{COLOR_SCHEMES['warning']}]")

        # Enhanced random generation with better color theory
        colors = []
        base_hue = random.randint(0, 360)
        
        for i in range(count):
            # Create harmonious colors using color theory
            if i == 0:
                hue = base_hue
            elif i == 1:
                hue = (base_hue + 180) % 360  # Complementary
            elif i == 2:
                hue = (base_hue + 120) % 360  # Triadic
            elif i == 3:
                hue = (base_hue + 240) % 360  # Triadic
            else:
                hue = (base_hue + (i * 30)) % 360  # Analogous variations
                
            # Convert HSV to RGB for better color control
            saturation = random.uniform(0.6, 0.9)
            value = random.uniform(0.5, 0.9)
            
            # Simple HSV to RGB conversion
            c = value * saturation
            x = c * (1 - abs((hue / 60) % 2 - 1))
            m = value - c
            
            if 0 <= hue < 60:
                r, g, b = c, x, 0
            elif 60 <= hue < 120:
                r, g, b = x, c, 0
            elif 120 <= hue < 180:
                r, g, b = 0, c, x
            elif 180 <= hue < 240:
                r, g, b = 0, x, c
            elif 240 <= hue < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
                
            r = int((r + m) * 255)
            g = int((g + m) * 255)
            b = int((b + m) * 255)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            colors.append(color)
            
        return colors

    def get_complementary_colors(self, base_color: str) -> List[str]:
        """Generate enhanced complementary color scheme"""
        hex_color = base_color.replace('#', '')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        colors = [f"#{hex_color}"]

        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b
        colors.append(f"#{comp_r:02x}{comp_g:02x}{comp_b:02x}")

        variations = [
            (min(255, r + 30), max(0, g - 15), b),
            (max(0, r - 30), min(255, g + 15), b),
            (r, g, min(255, b + 40)),
            (min(255, r + 15), min(255, g + 15), max(0, b - 20))
        ]
        
        for var_r, var_g, var_b in variations:
            colors.append(f"#{var_r:02x}{var_g:02x}{var_b:02x}")

        return colors[:5]  # Return max 5 colors

    def display_color_palette(self, colors: List[str], title: str = "Color Palette", show_ai_analysis: bool = False):
        """Display color palette in a beautiful format with optional AI analysis"""
        table = Table(
            title=f"🎨 {title}",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style=f"bold {COLOR_SCHEMES['primary']}"
        )
        
        table.add_column("Color", style="bold white", width=8)
        table.add_column("Preview", width=12)
        table.add_column("Hex", style=COLOR_SCHEMES['secondary'], width=10)
        table.add_column("RGB", style=COLOR_SCHEMES['accent'], width=15)
        table.add_column("HSL", style=COLOR_SCHEMES['warning'], width=15)

        for i, color in enumerate(colors):
            color_text = Text(f"  ████  ", style=f"on {color}")
            rgb_text = self.hex_to_rgb(color)
            hsl_text = self.hex_to_hsl(color)
            
            table.add_row(
                f"#{i+1}",
                color_text,
                color.upper(),
                rgb_text,
                hsl_text
            )

        console.print(table)
        
        harmony_panel = Panel.fit(
            self.get_color_harmony_info(colors),
            title="🎯 Color Harmony Analysis",
            border_style=COLOR_SCHEMES['secondary']
        )
        console.print("\n", harmony_panel)
        
        if show_ai_analysis:
            console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Getting AI analysis...[/{COLOR_SCHEMES['primary']}]")
            ai_analysis = self.ai.analyze_color_palette(colors)
            ai_panel = Panel.fit(
                ai_analysis,
                title="🤖 AI Color Analysis",
                border_style=COLOR_SCHEMES['accent']
            )
            console.print(ai_panel)

    def get_color_harmony_info(self, colors: List[str]) -> str:
        """Generate color harmony information"""
        info = []
        info.append("🎨 **Color Theory Insights:**")
        info.append(f"• Palette contains {len(colors)} colors")
        
        warm_colors = 0
        cool_colors = 0
        
        for color in colors:
            r, g, b = self.hex_to_rgb_values(color)
            if r > b and g > b:
                warm_colors += 1
            elif b > r and (b > g or g > r):
                cool_colors += 1
                
        if warm_colors > cool_colors:
            info.append("• **Temperature:** Warm palette (energetic, inviting)")
        elif cool_colors > warm_colors:
            info.append("• **Temperature:** Cool palette (calming, professional)")
        else:
            info.append("• **Temperature:** Balanced palette (versatile, harmonious)")
            
        info.append("• **Best for:** Web design, branding, print materials")
        info.append("• **Tip:** Test contrast ratios for accessibility compliance")
        
        return "\n".join(info)

    def hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex to RGB string"""
        hex_color = hex_color.replace('#', '')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"RGB({r}, {g}, {b})"
    
    def hex_to_rgb_values(self, hex_color: str) -> tuple:
        """Convert hex to RGB values"""
        hex_color = hex_color.replace('#', '')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def hex_to_hsl(self, hex_color: str) -> str:
        """Convert hex to HSL"""
        r, g, b = self.hex_to_rgb_values(hex_color)
        r, g, b = r/255.0, g/255.0, b/255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        l = (max_val + min_val) / 2
        
        if diff == 0:
            h = s = 0
        else:
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
            
            if max_val == r:
                h = ((g - b) / diff + (6 if g < b else 0)) / 6
            elif max_val == g:
                h = ((b - r) / diff + 2) / 6
            else:
                h = ((r - g) / diff + 4) / 6
                
        return f"HSL({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"

    def get_logo_from_api(self, logo_name: str = None, variant: str = None, version: str = None) -> Dict[str, Any]:
        """Get logo from Logotypes.dev API with enhanced error handling"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("🏷️ Fetching logo...", start=False)
                
                if logo_name:
                    url = f"https://www.logotypes.dev/{logo_name}"
                else:
                    url = "https://www.logotypes.dev/random"

                params = {}
                if variant:
                    params['variant'] = variant
                if version:
                    params['version'] = version

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    return {
                        'success': True,
                        'url': response.url,
                        'final_url': response.url,
                        'logo_name': logo_name or 'random',
                        'variant': variant,
                        'version': version
                    }
                else:
                    return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def display_logo_in_terminal(self, logo_url: str):
        """Enhanced logo display with better ASCII art"""
        try:
            from PIL import Image
            import io

            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img = img.convert('L')
                
                width, height = img.size
                aspect_ratio = height / width
                new_width = 80
                new_height = int(aspect_ratio * new_width * 0.45)
                img = img.resize((new_width, new_height))

                ascii_chars = "██▓▒░▒▓█▇▆▅▄▃▂▁ "
                ascii_art = []
                
                for y in range(new_height):
                    line = ""
                    for x in range(new_width):
                        pixel = img.getpixel((x, y))
                        char_index = min(len(ascii_chars) - 1, pixel // (256 // len(ascii_chars)))
                        line += ascii_chars[char_index]
                    ascii_art.append(line)

                console.print(Panel.fit(
                    "\n".join(ascii_art),
                    title=f"[bold {COLOR_SCHEMES['accent']}]🏷️ Logo Preview[/bold {COLOR_SCHEMES['accent']}]",
                    border_style=COLOR_SCHEMES['accent']
                ))
                return True
                
        except ImportError:
            console.print(f"[{COLOR_SCHEMES['warning']}]💡 Install Pillow for terminal logo display: pip install Pillow[/{COLOR_SCHEMES['warning']}]")
        except Exception as e:
            console.print(f"[{COLOR_SCHEMES['warning']}]Could not display logo: {str(e)}[/{COLOR_SCHEMES['warning']}]")

        return False

    def display_logo_result(self, logo_data: Dict[str, Any], show_in_terminal: bool = False):
        """Enhanced logo result display"""
        if logo_data['success']:
            table = Table(
                title=f"🏷️ Logo from Logotypes.dev",
                box=box.DOUBLE_EDGE,
                show_header=True,
                header_style=f"bold {COLOR_SCHEMES['primary']}"
            )
            table.add_column("Property", style=f"bold {COLOR_SCHEMES['secondary']}")
            table.add_column("Value", style="white")

            table.add_row("🏢 Brand Name", logo_data['logo_name'].title())
            table.add_row("🌐 URL", logo_data['url'])
            if logo_data.get('variant'):
                table.add_row("🎨 Variant", logo_data['variant'].title())
            if logo_data.get('version'):
                table.add_row("🎭 Version", logo_data['version'].title())

            console.print(table)

            if show_in_terminal:
                console.print(f"\n[{COLOR_SCHEMES['primary']}]Displaying logo in terminal...[/{COLOR_SCHEMES['primary']}]")
                success = self.display_logo_in_terminal(logo_data['url'])
                if not success:
                    console.print(f"[{COLOR_SCHEMES['success']}]✨ Access logo at: {logo_data['url']}[/{COLOR_SCHEMES['success']}]")
            else:
                console.print(f"[{COLOR_SCHEMES['success']}]✨ Access logo at: {logo_data['url']}[/{COLOR_SCHEMES['success']}]")

            if not show_in_terminal and Confirm.ask("\n🌐 Open logo in browser?", default=False):
                webbrowser.open(logo_data['url'])
        else:
            console.print(f"[{COLOR_SCHEMES['error']}]❌ Failed to get logo: {logo_data['error']}[/{COLOR_SCHEMES['error']}]")

    def generate_logo_ideas(self, business: str = "general") -> List[Dict[str, str]]:
        """Generate enhanced logo design ideas"""
        logo_styles = [
            {"style": "🔷 Minimalist", "description": "Clean lines, simple shapes, maximum impact with minimal elements"},
            {"style": "🏛️ Vintage", "description": "Retro aesthetics, aged textures, nostalgic color palettes"},
            {"style": "⚡ Modern Geometric", "description": "Sharp angles, bold shapes, contemporary mathematical precision"},
            {"style": "✏️ Hand-drawn", "description": "Organic textures, personal touch, artisanal authenticity"},
            {"style": "🔤 Typography-based", "description": "Custom lettering, font-focused design, typographic excellence"},
            {"style": "🎯 Icon + Text", "description": "Symbolic icon paired with brand name, balanced composition"},
            {"style": "🌀 Abstract", "description": "Non-literal shapes conveying brand essence and emotion"},
            {"style": "🎭 Mascot", "description": "Character-based design for friendly, approachable brand identity"},
            {"style": "🌈 Gradient Modern", "description": "Contemporary gradients, depth, digital-first aesthetic"},
            {"style": "📐 Architectural", "description": "Structural elements, strong foundations, professional appearance"}
        ]

        return random.sample(logo_styles, min(5, len(logo_styles)))

    def display_fonts(self, category: str):
        """Enhanced font display with better categorization"""
        if category not in FONT_CATEGORIES:
            console.print(f"[{COLOR_SCHEMES['error']}]Category '{category}' not found![/{COLOR_SCHEMES['error']}]")
            return

        table = Table(
            title=f"🔤 {category.title()} Fonts Collection",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style=f"bold {COLOR_SCHEMES['primary']}"
        )
        table.add_column("System Fonts", style=COLOR_SCHEMES['secondary'], width=20)
        table.add_column("Google Fonts", style=COLOR_SCHEMES['success'], width=20)
        table.add_column("Perfect For", style=COLOR_SCHEMES['accent'], width=25)
        table.add_column("Personality", style=COLOR_SCHEMES['warning'], width=20)

        system_fonts = FONT_CATEGORIES[category]
        google_fonts = GOOGLE_FONTS[category]

        use_cases = {
            "classic": ["Headlines & Headers", "Formal Documents", "Editorial Design", "Luxury Brands"],
            "modern": ["UI Interfaces", "Body Text", "Tech Companies", "Clean Layouts"],
            "playful": ["Children's Content", "Creative Brands", "Casual Designs", "Fun Projects"],
            "elegant": ["Fashion Brands", "Premium Products", "Editorial Design", "Art Galleries"],
            "tech": ["Code Display", "Developer Tools", "Technical Docs", "Programming"]
        }

        personalities = {
            "classic": ["Trustworthy", "Established", "Refined", "Traditional"],
            "modern": ["Clean", "Efficient", "Progressive", "Minimal"],
            "playful": ["Friendly", "Approachable", "Fun", "Creative"],
            "elegant": ["Sophisticated", "Luxurious", "Artistic", "Premium"],
            "tech": ["Precise", "Functional", "Technical", "Reliable"]
        }

        max_len = max(len(system_fonts), len(google_fonts), len(use_cases[category]), len(personalities[category]))

        for i in range(max_len):
            sys_font = system_fonts[i] if i < len(system_fonts) else ""
            goog_font = google_fonts[i] if i < len(google_fonts) else ""
            use_case = use_cases[category][i] if i < len(use_cases[category]) else ""
            personality = personalities[category][i] if i < len(personalities[category]) else ""
            table.add_row(sys_font, goog_font, use_case, personality)

        console.print(table)

        if category in ["modern", "classic"]:
            console.print(f"\n[{COLOR_SCHEMES['primary']}]💡 Pro Tip:[/{COLOR_SCHEMES['primary']}] {category.title()} fonts pair well with playful fonts for contrast!")

    def get_design_tips(self, count: int = 3, category: str = None) -> List[str]:
        """Get categorized design tips"""
        if category:
            category_tips = [tip for tip in DESIGN_TIPS if any(keyword in tip.lower() 
                           for keyword in self.get_category_keywords(category))]
            if category_tips:
                return random.sample(category_tips, min(count, len(category_tips)))
        
        return random.sample(DESIGN_TIPS, min(count, len(DESIGN_TIPS)))

    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for tip categories"""
        keywords = {
            "color": ["color", "palette", "contrast"],
            "typography": ["font", "text", "typography"],
            "layout": ["spacing", "grid", "layout", "whitespace"],
            "ux": ["user", "experience", "interaction", "accessibility"]
        }
        return keywords.get(category, [])

    def save_palette(self, colors: List[str], filename: str = None):
        """Enhanced palette saving with metadata"""
        if not filename:
            filename = f"palette_{random.randint(1000, 9999)}.json"

        palette_data = {
            "name": f"Designer CLI Palette {random.randint(100, 999)}",
            "colors": {
                "hex": colors,
                "rgb": [self.hex_to_rgb(color) for color in colors],
                "hsl": [self.hex_to_hsl(color) for color in colors]
            },
            "metadata": {
                "generated_at": "2025-07-02",
                "tool": "Designer CLI v2.0",
                "color_count": len(colors),
                "color_harmony": self.analyze_color_harmony(colors)
            },
            "usage_suggestions": [
                "Web design backgrounds and accents",
                "Brand identity development", 
                "Print material color schemes",
                "UI/UX design systems"
            ]
        }

        with open(filename, 'w') as f:
            json.dump(palette_data, f, indent=2)

        console.print(f"[{COLOR_SCHEMES['success']}]💾 Palette saved to {filename}[/{COLOR_SCHEMES['success']}]")

    def analyze_color_harmony(self, colors: List[str]) -> str:
        """Analyze color harmony type"""
        if len(colors) < 2:
            return "monochromatic"

        hues = []
        for color in colors:
            r, g, b = self.hex_to_rgb_values(color)
            r, g, b = r/255.0, g/255.0, b/255.0
            
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val
            
            if diff == 0:
                hue = 0
            elif max_val == r:
                hue = 60 * ((g - b) / diff)
            elif max_val == g:
                hue = 60 * ((b - r) / diff + 2)
            else:
                hue = 60 * ((r - g) / diff + 4)
                
            hues.append(hue % 360)
        
        hue_diff = max(hues) - min(hues)
        if hue_diff < 30:
            return "analogous"
        elif 150 < hue_diff < 210:
            return "complementary"
        elif 90 < hue_diff < 150:
            return "triadic"
        else:
            return "complex"

    def open_google_fonts(self):
        """Open Google Fonts in browser"""
        webbrowser.open("https://fonts.google.com")
        console.print(f"[{COLOR_SCHEMES['success']}]🌐 Opening Google Fonts in your browser...[/{COLOR_SCHEMES['success']}]")

    def interactive_color_builder(self):
        """Interactive color palette builder"""
        console.print(Panel.fit(
            "🎨 **Interactive Color Palette Builder**\n"
            "Build your perfect color scheme step by step!\n"
            "Choose base colors and let AI help you create harmony.",
            title="Color Builder",
            border_style=COLOR_SCHEMES['primary']
        ))
        
        colors = []
        while len(colors) < 6:
            if not colors:
                base_color = Prompt.ask(f"\n[{COLOR_SCHEMES['primary']}]Enter your base color (hex)[/{COLOR_SCHEMES['primary']}]", default="#3498db")
            else:
                console.print(f"\nCurrent palette: {', '.join(colors)}")
                choice = Prompt.ask(
                    f"[{COLOR_SCHEMES['secondary']}]Add another color (manual/ai/done)[/{COLOR_SCHEMES['secondary']}]",
                    choices=["manual", "ai", "done"],
                    default="done"
                )
                
                if choice == "done":
                    break
                elif choice == "manual":
                    base_color = Prompt.ask(f"[{COLOR_SCHEMES['primary']}]Enter color (hex)[/{COLOR_SCHEMES['primary']}]")
                else:  # ai
                    console.print(f"[{COLOR_SCHEMES['primary']}]🤖 AI suggesting complementary color...[/{COLOR_SCHEMES['primary']}]")
                    complementary = self.get_complementary_colors(colors[0])
                    base_color = complementary[len(colors) % len(complementary)]
                    console.print(f"AI suggests: {base_color}")
            
            if base_color.startswith('#') and len(base_color) == 7:
                colors.append(base_color)
                console.print(f"[{COLOR_SCHEMES['success']}]✅ Added {base_color}[/{COLOR_SCHEMES['success']}]")
            else:
                console.print(f"[{COLOR_SCHEMES['error']}]❌ Invalid hex color format[/{COLOR_SCHEMES['error']}]")
        
        if colors:
            self.display_color_palette(colors, "Your Custom Palette", show_ai_analysis=True)
            
            if Confirm.ask(f"\n[{COLOR_SCHEMES['secondary']}]Save this palette?[/{COLOR_SCHEMES['secondary']}]"):
                filename = Prompt.ask("Filename (without extension)", default="my_palette")
                self.save_palette(colors, f"{filename}.json")

@click.group()
@click.version_option("2.0.0")
def cli():
    """🎨 Designer's CLI Tool v2.0 - Your AI-powered creative companion!"""
    designer = DesignerCLI()
    designer.show_welcome_banner()

@cli.command()
@click.option('--count', '-c', default=5, help='Number of colors to generate')
@click.option('--save', '-s', help='Save palette to file')
@click.option('--base', '-b', help='Base color for complementary scheme')
@click.option('--search', help='Search ColorMagic API for themed palettes')
@click.option('--ai', is_flag=True, help='Get AI analysis of the palette')
@click.option('--interactive', '-i', is_flag=True, help='Interactive palette builder')
def palette(count, save, base, search, ai, interactive):
    """🌈 Generate beautiful color palettes with AI analysis"""
    designer = DesignerCLI()
    
    if interactive:
        designer.interactive_color_builder()
        return

    if base:
        colors = designer.get_complementary_colors(base)
        title = f"Complementary Palette (Base: {base})"
    elif search:
        colors = designer.generate_color_palette(count, search)
        title = f"ColorMagic Palette: '{search}'"
    else:
        colors = designer.generate_color_palette(count)
        title = "Harmonious Color Palette"

    designer.display_color_palette(colors, title, show_ai_analysis=ai)

    if save:
        designer.save_palette(colors, save)

@cli.command()
@click.argument('category', type=click.Choice(['classic', 'modern', 'playful', 'elegant', 'tech']))
@click.option('--ai-pairing', help='Get AI font pairing suggestions for specific font')
def fonts(category, ai_pairing):
    """🔤 Explore enhanced font collections with AI pairing suggestions"""
    designer = DesignerCLI()
    designer.display_fonts(category)
    
    if ai_pairing:
        console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Getting AI font pairing suggestions...[/{COLOR_SCHEMES['primary']}]")
        suggestions = designer.ai.suggest_font_pairing(ai_pairing, category)
        console.print(Panel.fit(
            suggestions,
            title=f"🤖 AI Font Pairing for {ai_pairing}",
            border_style=COLOR_SCHEMES['accent']
        ))

@cli.command()
@click.option('--business', '-b', default='general', help='Type of business for logo ideas')
@click.option('--name', '-n', help='Specific logo name (e.g. spotify, airbnb)')
@click.option('--variant', type=click.Choice(['glyph', 'wordmark']), help='Logo variant')
@click.option('--version', type=click.Choice(['black', 'white']), help='Logo version')
@click.option('--random', '-r', is_flag=True, help='Get random logo from API')
@click.option('--display', '-d', is_flag=True, help='Display logo in terminal (requires Pillow)')
@click.option('--ai-feedback', is_flag=True, help='Get AI feedback on logo design')
def logo(business, name, variant, version, random, display, ai_feedback):
    """🏷️ Generate logo ideas with AI feedback and real logos from Logotypes.dev"""
    designer = DesignerCLI()

    if name or random:
        logo_data = designer.get_logo_from_api(name, variant, version)
        designer.display_logo_result(logo_data, show_in_terminal=display)
        
        if ai_feedback and logo_data['success']:
            console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Getting AI logo analysis...[/{COLOR_SCHEMES['primary']}]")
            feedback = designer.ai.get_design_advice(f"Analyze the design principles of {logo_data['logo_name']} logo and provide professional feedback")
            console.print(Panel.fit(
                feedback,
                title=f"🤖 AI Logo Analysis: {logo_data['logo_name'].title()}",
                border_style=COLOR_SCHEMES['accent']
            ))
    else:
        ideas = designer.generate_logo_ideas(business)
        
        table = Table(
            title=f"🏷️ Logo Ideas for {business.title()} Business",
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style=f"bold {COLOR_SCHEMES['primary']}"
        )
        table.add_column("Style", style=f"bold {COLOR_SCHEMES['secondary']}")
        table.add_column("Description", style="white")

        for idea in ideas:
            table.add_row(idea["style"], idea["description"])

        console.print(table)
        
        console.print(Panel.fit(
            f"[{COLOR_SCHEMES['warning']}]💡 **Pro Tips:**[/{COLOR_SCHEMES['warning']}]\n"
            f"• Try `--random` for real logos from Logotypes.dev\n"
            f"• Use `--name spotify` for specific brand logos\n"
            f"• Add `--ai-feedback` for professional design analysis\n"
            f"• Use `--display` to preview logos in terminal",
            title="Logo Command Tips",
            border_style=COLOR_SCHEMES['secondary']
        ))

@cli.command()
@click.option('--count', '-c', default=3, help='Number of tips to show')
@click.option('--category', type=click.Choice(['color', 'typography', 'layout', 'ux']), help='Specific tip category')
def tips(count, category):
    """💡 Get categorized design tips and tricks"""
    designer = DesignerCLI()
    design_tips = designer.get_design_tips(count, category)
    
    title = f"💡 Design Tips" + (f" - {category.upper()}" if category else "")
    
    console.print(Panel.fit(
        "\n".join(design_tips),
        title=f"[bold {COLOR_SCHEMES['warning']}]{title}[/bold {COLOR_SCHEMES['warning']}]",
        border_style=COLOR_SCHEMES['warning']
    ))

@cli.command()
@click.argument('question', nargs=-1, required=True)
@click.option('--detailed', '-d', is_flag=True, help='Get detailed AI response')
def ask(question, detailed):
    """🤖 Ask the AI design assistant anything"""
    designer = DesignerCLI()
    question_text = ' '.join(question)
    
    console.print(Panel.fit(
        f"🤖 **AI Design Assistant**\n"
        f"**Your question:** {question_text}",
        title="Processing...",
        border_style=COLOR_SCHEMES['primary']
    ))
    
    if detailed:
        question_text += " Please provide a detailed, comprehensive response with examples and best practices."
    
    response = designer.ai.get_design_advice(question_text)
    
    console.print(Panel.fit(
        response,
        title=f"🤖 AI Design Assistant Response",
        border_style=COLOR_SCHEMES['accent']
    ))

@cli.command()
def google_fonts():
    """🌐 Open Google Fonts website"""
    designer = DesignerCLI()
    designer.open_google_fonts()

@cli.command()
def inspiration():
    """✨ Get complete AI-powered design inspiration package"""
    designer = DesignerCLI()

    console.print(Panel.fit(
        "🎨 **Generating Your Personal Design Inspiration Package**\n"
        "This includes: themed palette, fonts, logo inspiration, and AI insights!",
        title="Inspiration Generator",
        border_style=COLOR_SCHEMES['primary']
    ))

    themes = ['nature', 'ocean', 'sunset', 'modern', 'vintage', 'minimal', 'vibrant', 'pastel', 'neon', 'earth']
    theme = random.choice(themes)
    colors = designer.generate_color_palette(5, theme)
    designer.display_color_palette(colors, f"🌈 {theme.title()} Inspiration Palette", show_ai_analysis=True)

    category = random.choice(list(FONT_CATEGORIES.keys()))
    console.print(f"\n[bold {COLOR_SCHEMES['secondary']}]🔤 Recommended Font Category: {category.title()}[/bold {COLOR_SCHEMES['secondary']}]")
    fonts_list = random.sample(GOOGLE_FONTS[category], 3)
    
    font_table = Table(box=box.SIMPLE, show_header=False)
    font_table.add_column("Font", style=COLOR_SCHEMES['success'])
    for font in fonts_list:
        font_table.add_row(f"• {font}")
    console.print(font_table)

    primary_font = fonts_list[0]
    console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Getting AI font pairing for {primary_font}...[/{COLOR_SCHEMES['primary']}]")
    font_pairing = designer.ai.suggest_font_pairing(primary_font, category)
    console.print(Panel.fit(
        font_pairing,
        title=f"🤖 AI Font Pairing Suggestions",
        border_style=COLOR_SCHEMES['accent']
    ))

    console.print(f"\n[bold {COLOR_SCHEMES['secondary']}]🏷️ Logo Inspiration:[/bold {COLOR_SCHEMES['secondary']}]")
    logo_data = designer.get_logo_from_api()
    if logo_data['success']:
        console.print(f"  📱 Inspirational Logo: {logo_data['url']}")
        
        if Confirm.ask("🖼️ Preview logo in terminal?", default=False):
            designer.display_logo_in_terminal(logo_data['url'])

    logo_ideas = designer.generate_logo_ideas()
    selected_style = logo_ideas[0]
    console.print(f"\n[bold {COLOR_SCHEMES['secondary']}]🎨 Recommended Logo Style: {selected_style['style']}[/bold {COLOR_SCHEMES['secondary']}]")
    console.print(f"  {selected_style['description']}")

    console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Getting personalized design insight...[/{COLOR_SCHEMES['primary']}]")
    insight_prompt = f"Provide a creative design insight for a {theme} themed project using {category} fonts and {selected_style['style'].lower()} logo style"
    insight = designer.ai.get_design_advice(insight_prompt)
    console.print(Panel.fit(
        insight,
        title="🤖 Personalized Design Insight",
        border_style=COLOR_SCHEMES['accent']
    ))

    tip = designer.get_design_tips(1)[0]
    console.print(Panel.fit(
        tip,
        title=f"[bold {COLOR_SCHEMES['warning']}]💡 Pro Design Tip[/bold {COLOR_SCHEMES['warning']}]",
        border_style=COLOR_SCHEMES['warning']
    ))

@cli.command()
def all_fonts():
    """📚 Show all font categories with enhanced display"""
    designer = DesignerCLI()
    categories = ['classic', 'modern', 'playful', 'elegant', 'tech']
    
    for i, category in enumerate(categories):
        if i > 0:
            console.print("\n" + "─" * 80)
        designer.display_fonts(category)

@cli.command()
@click.argument('brand_name')
@click.option('--variant', type=click.Choice(['glyph', 'wordmark']), help='Logo variant type')
@click.option('--version', type=click.Choice(['black', 'white']), help='Logo color version')
@click.option('--open', '-o', is_flag=True, help='Open logo in browser automatically')
@click.option('--display', '-d', is_flag=True, help='Display logo in terminal (requires Pillow)')
@click.option('--ai-analysis', is_flag=True, help='Get AI design analysis of the logo')
def get_logo(brand_name, variant, version, open, display, ai_analysis):
    """🔍 Get specific brand logo with AI analysis"""
    designer = DesignerCLI()
    logo_data = designer.get_logo_from_api(brand_name, variant, version)
    designer.display_logo_result(logo_data, show_in_terminal=display)

    if ai_analysis and logo_data['success']:
        console.print(f"\n[{COLOR_SCHEMES['primary']}]🤖 Analyzing {brand_name} logo design...[/{COLOR_SCHEMES['primary']}]")
        analysis = designer.ai.get_design_advice(f"Provide a professional design analysis of {brand_name}'s logo, covering design principles, effectiveness, and brand representation")
        console.print(Panel.fit(
            analysis,
            title=f"🤖 Professional Logo Analysis: {brand_name.title()}",
            border_style=COLOR_SCHEMES['accent']
        ))

    if open and logo_data['success']:
        webbrowser.open(logo_data['url'])

@cli.command()
def explore_logos():
    """🎯 Explore available logo options with AI insights"""
    designer = DesignerCLI()
    
    console.print(Panel.fit(
        f"[bold {COLOR_SCHEMES['primary']}]🏷️ Logotypes.dev API Explorer[/bold {COLOR_SCHEMES['primary']}]\n\n"
        f"[{COLOR_SCHEMES['secondary']}]**Popular brands available:**[/{COLOR_SCHEMES['secondary']}]\n"
        f"• **Tech:** spotify, airbnb, google, apple, microsoft\n"
        f"• **Social:** github, twitter, instagram, facebook, discord\n"
        f"• **Business:** netflix, amazon, tesla, uber, zoom, slack\n"
        f"• **Design:** figma, adobe, sketch, canva, dribbble\n\n"
        f"[{COLOR_SCHEMES['warning']}]**Variants & Versions:**[/{COLOR_SCHEMES['warning']}]\n"
        f"• **glyph** (icon only) | **wordmark** (text/brand name)\n"
        f"• **black** (dark version) | **white** (light version)\n\n"
        f"[{COLOR_SCHEMES['success']}]**Enhanced Examples:**[/{COLOR_SCHEMES['success']}]\n"
        f"• `designer get-logo spotify --ai-analysis`\n"
        f"• `designer get-logo airbnb --variant wordmark --display`\n"
        f"• `designer logo --random --ai-feedback`\n"
        f"• `designer get-logo google --version black --open`",
        border_style=COLOR_SCHEMES['accent']
    ))

@cli.command()
def interactive():
    """🎮 Launch interactive design session"""
    designer = DesignerCLI()
    
    console.print(Panel.fit(
        f"[bold {COLOR_SCHEMES['primary']}]🎮 Interactive Design Session[/bold {COLOR_SCHEMES['primary']}]\n"
        f"Let's create something amazing together!",
        border_style=COLOR_SCHEMES['primary']
    ))
    
    while True:
        console.print(f"\n[{COLOR_SCHEMES['secondary']}]What would you like to do?[/{COLOR_SCHEMES['secondary']}]")
        choices = [
            "🎨 Build custom color palette",
            "🤖 Ask AI design question", 
            "🏷️ Get random logo inspiration",
            "💡 Get design tips",
            "✨ Generate complete inspiration package",
            "🚪 Exit"
        ]
        
        for i, choice in enumerate(choices, 1):
            console.print(f"  {i}. {choice}")
        
        selection = Prompt.ask(
            f"[{COLOR_SCHEMES['primary']}]Choose option (1-6)[/{COLOR_SCHEMES['primary']}]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="6"
        )
        
        if selection == "1":
            designer.interactive_color_builder()
        elif selection == "2":
            question = Prompt.ask(f"[{COLOR_SCHEMES['primary']}]What's your design question?[/{COLOR_SCHEMES['primary']}]")
            response = designer.ai.get_design_advice(question)
            console.print(Panel.fit(response, title="🤖 AI Response", border_style=COLOR_SCHEMES['accent']))
        elif selection == "3":
            logo_data = designer.get_logo_from_api()
            designer.display_logo_result(logo_data, show_in_terminal=True)
        elif selection == "4":
            tips = designer.get_design_tips(3)
            console.print(Panel.fit("\n".join(tips), title="💡 Design Tips", border_style=COLOR_SCHEMES['warning']))
        elif selection == "5":
            theme = random.choice(['modern', 'vintage', 'minimal', 'vibrant'])
            colors = designer.generate_color_palette(4, theme)
            designer.display_color_palette(colors, f"{theme.title()} Inspiration")
        else:
            console.print(f"[{COLOR_SCHEMES['success']}]✨ Happy designing![/{COLOR_SCHEMES['success']}]")
            break

if __name__ == '__main__':
    cli()
