#!/usr/bin/env python3
"""
Enhanced Studio Voice CLI
An interactive command-line interface with better UX for Studio Voice processing
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint
import time

console = Console()

class StudioVoiceCLI:
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.studio_voice_script = self.script_dir / "scripts" / "studio_voice.py"
        self.venv_activate = self.script_dir / "nim" / "Scripts" / "activate.bat"
        
    def show_banner(self):
        """Display the application banner"""
        banner = Panel.fit(
            "[bold cyan]🎵 Studio Voice Enhanced CLI[/bold cyan]\n"
            "[dim]AI-Powered Audio Enhancement with Interactive Interface[/dim]",
            border_style="cyan"
        )
        console.print(banner)
        console.print()
        
    def check_prerequisites(self):
        """Check if all required components are available"""
        issues = []
        
        if not self.studio_voice_script.exists():
            issues.append(f"Studio Voice script not found: {self.studio_voice_script}")
            
        if not self.venv_activate.exists():
            issues.append(f"Virtual environment not found: {self.venv_activate}")
            
        if issues:
            console.print("[red]❌ Prerequisites check failed:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            return False
            
        console.print("[green]✅ Prerequisites check passed[/green]")
        return True
        
    def select_files_interactive(self):
        """Interactive file selection"""
        console.print("\n[bold]File Selection Options:[/bold]")
        console.print("1. Single file")
        console.print("2. Multiple files (space-separated)")
        console.print("3. Directory (recursive scan)")
        console.print("4. Pattern matching (e.g., *.wav)")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            file_path = Prompt.ask("Enter file path")
            return [file_path] if os.path.exists(file_path) else []
            
        elif choice == "2":
            files_input = Prompt.ask("Enter file paths (space-separated)")
            files = [f.strip() for f in files_input.split()]
            return [f for f in files if os.path.exists(f)]
            
        elif choice == "3":
            directory = Prompt.ask("Enter directory path")
            if os.path.isdir(directory):
                audio_extensions = {'.wav', '.mp3', '.flac', '.m4a'}
                files = []
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames:
                        if Path(filename).suffix.lower() in audio_extensions:
                            files.append(os.path.join(root, filename))
                return files
            return []
            
        elif choice == "4":
            import glob
            pattern = Prompt.ask("Enter file pattern (e.g., *.wav)")
            return glob.glob(pattern, recursive=True)
            
        return []
        
    def configure_settings_interactive(self):
        """Interactive settings configuration"""
        console.print("\n[bold]Processing Configuration:[/bold]")
        
        # Model type selection
        model_options = {
            "1": ("48k-hq", "48kHz High Quality (recommended)"),
            "2": ("48k-ll", "48kHz Low Latency"),
            "3": ("16k-hq", "16kHz High Quality")
        }
        
        console.print("\nModel Types:")
        for key, (model, desc) in model_options.items():
            console.print(f"{key}. {desc}")
            
        model_choice = Prompt.ask("Select model type", choices=["1", "2", "3"], default="1")
        model_type = model_options[model_choice][0]
        
        # Streaming mode
        streaming = Confirm.ask("Enable streaming mode?", default=False)
        
        # Server settings
        default_server = "127.0.0.1:8001"
        server = Prompt.ask(f"Server address", default=default_server)
        
        # Output settings
        output_dir = Prompt.ask("Output directory", default="./enhanced_audio")
        
        return {
            'model_type': model_type,
            'streaming': streaming,
            'server': server,
            'output_dir': output_dir
        }
        
    def show_file_summary(self, files, settings):
        """Display a summary of files and settings"""
        table = Table(title="Processing Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files to process", str(len(files)))
        table.add_row("Model type", settings['model_type'])
        table.add_row("Streaming mode", "Yes" if settings['streaming'] else "No")
        table.add_row("Server", settings['server'])
        table.add_row("Output directory", settings['output_dir'])
        
        console.print(table)
        
        if len(files) <= 10:
            console.print("\n[bold]Files to process:[/bold]")
            for i, file in enumerate(files, 1):
                console.print(f"  {i}. {os.path.basename(file)}")
        else:
            console.print(f"\n[bold]Files to process:[/bold] {len(files)} files")
            console.print("  (Too many to list individually)")
            
    def process_files(self, files, settings):
        """Process files with enhanced progress display"""
        os.makedirs(settings['output_dir'], exist_ok=True)
        
        successful = 0
        failed = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            overall_task = progress.add_task("Overall Progress", total=len(files))
            
            for i, input_file in enumerate(files):
                filename = os.path.basename(input_file)
                current_task = progress.add_task(f"Processing {filename}", total=100)
                
                try:
                    # Create output filename
                    output_file = os.path.join(settings['output_dir'], f"enhanced_{filename}")
                    
                    # Build command
                    cmd = [
                        'python', str(self.studio_voice_script),
                        '--input', input_file,
                        '--output', output_file,
                        '--model-type', settings['model_type'],
                        '--target', settings['server']
                    ]
                    
                    if settings['streaming']:
                        cmd.append('--streaming')
                    
                    # Simulate progress (in real implementation, you'd parse actual progress)
                    for step in range(0, 101, 10):
                        progress.update(current_task, completed=step)
                        time.sleep(0.1)  # Simulate processing time
                    
                    # Run the actual command
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    progress.update(current_task, completed=100)
                    
                    if result.returncode == 0:
                        successful += 1
                        progress.update(current_task, description=f"✅ {filename}")
                    else:
                        failed += 1
                        progress.update(current_task, description=f"❌ {filename}")
                        console.print(f"[red]Error processing {filename}: {result.stderr}[/red]")
                        
                except subprocess.TimeoutExpired:
                    failed += 1
                    progress.update(current_task, description=f"⏰ {filename} (timeout)")
                except Exception as e:
                    failed += 1
                    progress.update(current_task, description=f"❌ {filename}")
                    console.print(f"[red]Error processing {filename}: {str(e)}[/red]")
                
                progress.update(overall_task, advance=1)
                progress.remove_task(current_task)
        
        return successful, failed
        
    def show_results(self, successful, failed, output_dir):
        """Display processing results"""
        console.print()
        
        if successful > 0:
            panel = Panel(
                f"[green]✅ Successfully processed {successful} files[/green]\n"
                f"[dim]Enhanced files saved to: {output_dir}[/dim]",
                title="Processing Complete",
                border_style="green"
            )
        else:
            panel = Panel(
                f"[red]❌ No files were successfully processed[/red]\n"
                f"[dim]Failed: {failed} files[/dim]",
                title="Processing Failed",
                border_style="red"
            )
            
        console.print(panel)
        
        if failed > 0:
            console.print(f"[yellow]⚠️  {failed} files failed to process[/yellow]")
            
    def run_interactive_mode(self):
        """Run the interactive CLI mode"""
        self.show_banner()
        
        if not self.check_prerequisites():
            return 1
            
        # File selection
        console.print("\n[bold blue]Step 1: File Selection[/bold blue]")
        files = self.select_files_interactive()
        
        if not files:
            console.print("[red]❌ No valid files selected[/red]")
            return 1
            
        console.print(f"[green]✅ Selected {len(files)} files[/green]")
        
        # Settings configuration
        console.print("\n[bold blue]Step 2: Configuration[/bold blue]")
        settings = self.configure_settings_interactive()
        
        # Summary and confirmation
        console.print("\n[bold blue]Step 3: Review & Confirm[/bold blue]")
        self.show_file_summary(files, settings)
        
        if not Confirm.ask("\nProceed with processing?", default=True):
            console.print("[yellow]Processing cancelled[/yellow]")
            return 0
            
        # Processing
        console.print("\n[bold blue]Step 4: Processing[/bold blue]")
        successful, failed = self.process_files(files, settings)
        
        # Results
        self.show_results(successful, failed, settings['output_dir'])
        
        return 0 if successful > 0 else 1
        
    def run_batch_mode(self, args):
        """Run in batch mode with command line arguments"""
        # Process files using the provided arguments
        files = []
        
        if args.input:
            if os.path.isfile(args.input):
                files = [args.input]
            elif os.path.isdir(args.input):
                audio_extensions = {'.wav', '.mp3', '.flac', '.m4a'}
                for root, dirs, filenames in os.walk(args.input):
                    for filename in filenames:
                        if Path(filename).suffix.lower() in audio_extensions:
                            files.append(os.path.join(root, filename))
                            
        if not files:
            console.print("[red]❌ No valid input files found[/red]")
            return 1
            
        settings = {
            'model_type': args.model_type,
            'streaming': args.streaming,
            'server': args.target,
            'output_dir': args.output or './enhanced_audio'
        }
        
        console.print(f"[cyan]Processing {len(files)} files in batch mode...[/cyan]")
        successful, failed = self.process_files(files, settings)
        self.show_results(successful, failed, settings['output_dir'])
        
        return 0 if successful > 0 else 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Studio Voice CLI with interactive features"
    )
    parser.add_argument('--input', '-i', help='Input file or directory')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--model-type', '-m', default='48k-hq', 
                       choices=['48k-hq', '48k-ll', '16k-hq'],
                       help='Model type to use')
    parser.add_argument('--streaming', '-s', action='store_true',
                       help='Enable streaming mode')
    parser.add_argument('--target', '-t', default='127.0.0.1:8001',
                       help='Server target address')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Run in batch mode (non-interactive)')
    
    args = parser.parse_args()
    
    cli = StudioVoiceCLI()
    
    try:
        if args.batch or args.input:
            return cli.run_batch_mode(args)
        else:
            return cli.run_interactive_mode()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
