# Bare React Native Before/After Examples

Real-world transformations for projects using React Native CLI (non-Expo) or ejected Expo projects.

---

## Example 1: Chat Message List

### Before

```tsx
import React from 'react';
import {
  View, Text, FlatList, TextInput, Pressable, Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

function ChatScreen({ messages, currentUser }) {
  const [text, setText] = useState('');

  const renderMessage = ({ item }) => (
    <Pressable onLongPress={() => showMessageOptions(item)}>
      <View style={styles.messageRow}>
        <Image source={{ uri: item.sender.avatar }} style={styles.avatar} />
        <View>
          <Text style={{ fontSize: 12, color: '#bbb' }}>{item.sender.name}</Text>
          <Text>{item.text}</Text>
          <Text style={{ fontSize: 10, color: '#ddd' }}>{item.timestamp}</Text>
        </View>
      </View>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>Chat</Text>

      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
      />

      <View style={styles.inputRow}>
        <TextInput
          value={text}
          onChangeText={setText}
          placeholder="Type a message..."
          style={styles.input}
        />
        <Pressable onPress={sendMessage} style={{ width: 32, height: 32 }}>
          <Icon name="send" size={24} color="#007AFF" />
        </Pressable>
      </View>
    </View>
  );
}
```

### After

```tsx
import React from 'react';
import {
  View, Text, FlatList, TextInput, Pressable, Image, AccessibilityInfo,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

function ChatScreen({ messages, currentUser }) {
  const [text, setText] = useState('');

  const renderMessage = ({ item }) => (
    <Pressable
      onLongPress={() => showMessageOptions(item)}
      accessibilityLabel={`${item.sender.name}: ${item.text}, ${item.timestamp}`}
      accessibilityRole="button"
      accessibilityHint="Shows message options" // [VERIFY] confirm hint accuracy
      accessibilityActions={[
        { name: 'reply', label: 'Reply' },
        { name: 'copy', label: 'Copy text' },
        { name: 'delete', label: 'Delete message' },
      ]}
      onAccessibilityAction={(event) => {
        switch (event.nativeEvent.actionName) {
          case 'reply': replyToMessage(item); break;
          case 'copy': copyMessageText(item); break;
          case 'delete': deleteMessage(item.id); break;
        }
      }}
    >
      <View style={styles.messageRow}>
        <Image
          source={{ uri: item.sender.avatar }}
          style={styles.avatar}
          accessible={false}
        />
        <View>
          <Text style={{ fontSize: 12, color: '#767676' }}>
            {/* [VERIFY] contrast ratio of #767676 on background meets 4.5:1 */}
            {item.sender.name}
          </Text>
          <Text>{item.text}</Text>
          <Text style={{ fontSize: 10, color: '#767676' }}>
            {/* [VERIFY] contrast ratio meets 4.5:1 */}
            {item.timestamp}
          </Text>
        </View>
      </View>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      <Text
        style={{ fontSize: 20, fontWeight: 'bold' }}
        accessibilityRole="header"
      >
        Chat
      </Text>

      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
      />

      <View style={styles.inputRow}>
        <TextInput
          value={text}
          onChangeText={setText}
          placeholder="Type a message..."
          style={styles.input}
          accessibilityLabel="Message"
          accessibilityHint="Type your message here"
        />
        <Pressable
          onPress={sendMessage}
          style={{ width: 32, height: 32 }}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          accessibilityLabel="Send message" // [VERIFY] confirm label matches intent
          accessibilityRole="button"
        >
          <Icon name="send" size={24} color="#007AFF" />
        </Pressable>
      </View>
    </View>
  );
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Icon-only send button without label | Added `accessibilityLabel` + `accessibilityRole` |
| P0 | Avatar images without labels | Hidden with `accessible={false}` (parent has composed label) |
| P1 | Send button below 48x48 | Added `hitSlop` to expand touch target |
| P1 | TextInput without label | Added `accessibilityLabel` + `accessibilityHint` |
| P1 | Message pressable without role | Added `accessibilityRole="button"` |
| P2 | "Chat" heading without header role | Added `accessibilityRole="header"` |
| P2 | Long-press without custom actions | Added `accessibilityActions` + `onAccessibilityAction` |
| P2 | `#bbb` and `#ddd` text fails contrast | Changed to `#767676` with `[VERIFY]` |

---

## Example 2: Custom Modal with Bottom Sheet

### Before

```tsx
import React, { useState, useRef } from 'react';
import { View, Text, Pressable, Animated, Dimensions } from 'react-native';
import Icon from 'react-native-vector-icons/Feather';

function ConfirmDialog({ visible, onConfirm, onCancel, message }) {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <Pressable style={styles.backdrop} onPress={onCancel} />
      <View style={styles.dialog}>
        <Text style={{ fontSize: 18, fontWeight: 'bold' }}>{message}</Text>

        <View style={styles.buttonRow}>
          <Pressable onPress={onCancel} style={styles.cancelButton}>
            <Text>Cancel</Text>
          </Pressable>
          <Pressable onPress={onConfirm} style={styles.confirmButton}>
            <Text style={{ color: 'white' }}>Confirm</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

function ParentScreen() {
  const [showDialog, setShowDialog] = useState(false);

  return (
    <View>
      <Text>Main Content</Text>
      <Pressable onPress={() => setShowDialog(true)}>
        <Icon name="trash-2" size={20} />
      </Pressable>
      <ConfirmDialog
        visible={showDialog}
        message="Delete this item?"
        onConfirm={handleDelete}
        onCancel={() => setShowDialog(false)}
      />
    </View>
  );
}
```

### After

```tsx
import React, { useState, useRef } from 'react';
import { View, Text, Pressable, Animated, Dimensions, AccessibilityInfo } from 'react-native';
import Icon from 'react-native-vector-icons/Feather';

function ConfirmDialog({ visible, onConfirm, onCancel, message }) {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <Pressable
        style={styles.backdrop}
        onPress={onCancel}
        accessible={false}
        importantForAccessibility="no"
      />
      <View
        style={styles.dialog}
        accessibilityViewIsModal={true}
        accessibilityRole="alert"
      >
        <Text
          style={{ fontSize: 18, fontWeight: 'bold' }}
          accessibilityRole="header"
        >
          {message}
        </Text>

        <View style={styles.buttonRow}>
          <Pressable
            onPress={onCancel}
            style={styles.cancelButton}
            accessibilityRole="button"
          >
            <Text>Cancel</Text>
          </Pressable>
          <Pressable
            onPress={onConfirm}
            style={styles.confirmButton}
            accessibilityRole="button"
          >
            <Text style={{ color: 'white' }}>Confirm</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

function ParentScreen() {
  const [showDialog, setShowDialog] = useState(false);
  const triggerRef = useRef(null);

  return (
    <View
      importantForAccessibility={showDialog ? 'no-hide-descendants' : 'auto'}
      accessibilityElementsHidden={showDialog}
    >
      <Text>Main Content</Text>
      <Pressable
        ref={triggerRef}
        onPress={() => setShowDialog(true)}
        accessibilityLabel="Delete item" // [VERIFY] confirm label matches intent
        accessibilityRole="button"
        accessibilityHint="Opens a confirmation dialog" // [VERIFY] confirm hint accuracy
      >
        <Icon name="trash-2" size={20} />
      </Pressable>
      <ConfirmDialog
        visible={showDialog}
        message="Delete this item?"
        onConfirm={handleDelete}
        onCancel={() => {
          setShowDialog(false);
          triggerRef.current?.focus();
        }}
      />
    </View>
  );
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Icon-only delete button without label | Added `accessibilityLabel` + `accessibilityRole` |
| P1 | Delete button without hint | Added `accessibilityHint` |
| P1 | Dialog buttons without roles | Added `accessibilityRole="button"` |
| P2 | Dialog heading without header role | Added `accessibilityRole="header"` |
| P2 | Custom modal without focus management | Added `accessibilityViewIsModal`, background hiding, focus return |
| P2 | Backdrop reachable by screen readers | Hidden with `accessible={false}` + `importantForAccessibility="no"` |

---

## Bare RN vs Expo — Key Differences

For accessibility purposes, bare React Native and Expo are nearly identical. The differences are:

| Feature | Expo Managed | Bare React Native |
|---------|-------------|-------------------|
| Image component | `expo-image` or RN `Image` — both support `accessibilityLabel` | RN `Image` — supports `accessibilityLabel` |
| Icons | `@expo/vector-icons` — use icon name to infer labels | `react-native-vector-icons` or SVG — same approach |
| Navigation | `expo-router` — adds `<Stack.Screen options>` | `@react-navigation` — adds `screenOptions` |
| Config | `app.json` / `app.config.js` for orientation | `Info.plist` (iOS) / `AndroidManifest.xml` (Android) |
| Native modules | Access via config plugins | Direct native code access |

All React Native accessibility props (`accessibilityLabel`, `accessibilityRole`, `accessibilityState`, etc.) work identically in both environments.
