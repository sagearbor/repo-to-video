#!/usr/bin/env python3
"""
Helper script to read and update DEVELOPER_CHECKLIST.yaml
"""
import yaml
import sys
from pathlib import Path
from datetime import datetime

CHECKLIST_FILE = Path(__file__).parent / "docs" / "DEVELOPER_CHECKLIST.yaml"


def load_checklist():
    """Load the checklist YAML file"""
    with open(CHECKLIST_FILE, 'r') as f:
        return yaml.safe_load(f)


def save_checklist(data):
    """Save the checklist YAML file"""
    with open(CHECKLIST_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def show_next_steps():
    """Display the next immediate steps"""
    data = load_checklist()
    next_steps = data.get('next_steps', [])

    print("=" * 70)
    print("NEXT IMMEDIATE STEPS")
    print("=" * 70)

    for step in next_steps:
        print(f"\n{step['step']}. {step['task']}")
        print(f"   Priority: {step['priority']}")
        print(f"   Estimated time: {step['estimated_time']}")

        if 'command' in step:
            print(f"   Command: {step['command']}")

        if 'notes' in step:
            print(f"   Notes: {step['notes']}")

        if 'subtasks' in step:
            print("   Subtasks:")
            for subtask in step['subtasks']:
                print(f"     - {subtask}")


def show_blockers():
    """Display current blockers"""
    data = load_checklist()
    blockers = data['metadata'].get('current_blockers', [])

    print("=" * 70)
    print("CURRENT BLOCKERS")
    print("=" * 70)

    if not blockers:
        print("No blockers! 🎉")
    else:
        for i, blocker in enumerate(blockers, 1):
            print(f"{i}. {blocker}")


def show_issues():
    """Display known issues"""
    data = load_checklist()
    issues = data.get('issues', [])

    print("=" * 70)
    print("KNOWN ISSUES")
    print("=" * 70)

    open_issues = [i for i in issues if i['status'] == 'open']

    if not open_issues:
        print("No open issues! 🎉")
    else:
        for issue in open_issues:
            print(f"\n[{issue['id']}] {issue['title']}")
            print(f"   Severity: {issue['severity']}")
            print(f"   Description: {issue['description']}")

            if 'solution' in issue:
                print(f"   Solution: {issue['solution']}")

            if 'blockers' in issue and issue['blockers']:
                print(f"   Blocked by: {', '.join(issue['blockers'])}")


def show_progress():
    """Display overall progress"""
    data = load_checklist()
    metadata = data['metadata']

    print("=" * 70)
    print(f"PROJECT: {metadata['project_name']}")
    print("=" * 70)
    print(f"Current Phase: {metadata['current_phase']}")
    print(f"MVP Completion: {metadata['mvp_completion']}%")
    print(f"Last Updated: {metadata['last_updated']}")


def show_session_notes():
    """Display session notes"""
    data = load_checklist()
    notes = data.get('session_notes', [])

    print("=" * 70)
    print("SESSION NOTES")
    print("=" * 70)

    for note in notes:
        print(f"\n📅 {note['date']}")
        print(f"Summary: {note['summary']}")

        if note.get('completed'):
            print("Completed:")
            for item in note['completed']:
                print(f"  ✓ {item}")

        if note.get('blockers_identified'):
            print("Blockers Identified:")
            for blocker in note['blockers_identified']:
                print(f"  ⚠️  {blocker}")

        if note.get('next_session_start_here'):
            print(f"Next session: {note['next_session_start_here']}")


def add_session_note(summary):
    """Add a new session note"""
    data = load_checklist()

    if 'session_notes' not in data:
        data['session_notes'] = []

    note = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'summary': summary,
        'completed': [],
        'blockers_identified': [],
        'next_session_start_here': ''
    }

    data['session_notes'].append(note)
    save_checklist(data)

    print(f"✓ Added session note for {note['date']}")


def show_stage_status(stage):
    """Show status of a specific stage"""
    data = load_checklist()

    stage_map = {
        '0': 'stage0_analysis',
        '1': 'stage1_capture',
        '2': 'stage2_audio',
        '3': 'stage3_standardize',
        '4': 'stage4_assembly'
    }

    stage_key = stage_map.get(stage)
    if not stage_key:
        print(f"Unknown stage: {stage}")
        return

    stage_data = data.get(stage_key, {})

    print("=" * 70)
    print(f"STAGE {stage} STATUS")
    print("=" * 70)

    for section_name, section_data in stage_data.items():
        status = section_data.get('status', 'unknown')
        priority = section_data.get('priority', 'unknown')

        print(f"\n{section_name.replace('_', ' ').title()}")
        print(f"  Status: {status}")
        print(f"  Priority: {priority}")

        if 'notes' in section_data:
            print(f"  Notes: {section_data['notes']}")

        if 'blocker_reason' in section_data:
            print(f"  Blocker: {section_data['blocker_reason']}")

        if 'items' in section_data:
            items = section_data['items']
            completed = sum(1 for item in items if item.get('status') == 'complete')
            total = len(items)
            print(f"  Progress: {completed}/{total} items complete")


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python checklist.py <command>")
        print("\nCommands:")
        print("  progress      - Show overall progress")
        print("  next          - Show next immediate steps")
        print("  blockers      - Show current blockers")
        print("  issues        - Show known issues")
        print("  notes         - Show session notes")
        print("  stage <0-4>   - Show status of specific stage")
        print("  note <text>   - Add a session note")
        return

    command = sys.argv[1]

    if command == 'progress':
        show_progress()
    elif command == 'next':
        show_next_steps()
    elif command == 'blockers':
        show_blockers()
    elif command == 'issues':
        show_issues()
    elif command == 'notes':
        show_session_notes()
    elif command == 'stage' and len(sys.argv) > 2:
        show_stage_status(sys.argv[2])
    elif command == 'note' and len(sys.argv) > 2:
        summary = ' '.join(sys.argv[2:])
        add_session_note(summary)
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments for help")


if __name__ == "__main__":
    main()
